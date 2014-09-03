#
# Copyright (c) 2013-2014 QuarksLab.
# This file is part of IRMA project.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License in the top-level directory
# of this distribution and at:
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# No part of the project, including this file, may be copied,
# modified, propagated, or distributed except according to the
# terms contained in the LICENSE file.

import hashlib
import logging
from frontend.models.nosqlobjects import ProbeRealResult
from frontend.models.sqlobjects import Scan, File, FileWeb, ProbeResult
from lib.common import compat
from lib.irma.common.utils import IrmaReturnCode, IrmaScanStatus, \
    IrmaProbeResultsStates
from lib.irma.common.exceptions import IrmaCoreError, \
    IrmaDatabaseResultNotFound, IrmaValueError, IrmaTaskError, \
    IrmaFtpError
from frontend.format import IrmaFormatter
from frontend.helpers.sql import session_transaction, session_query
import frontend.controllers.braintasks as celery_brain
import frontend.controllers.ftpctrl as ftp_ctrl


log = logging.getLogger()
log.setLevel(logging.DEBUG)

# =========
#  Helpers
# =========

def format_results(res_dict, filter_type):
    # - filter type is list of type returned
    res = {}
    for (name, results) in res_dict.items():
        res[name] = IrmaFormatter.format(name, results)
    # filter by type
    if filter_type is not None:
        res = dict((k, v) for k, v in res.items() if v['type'] in filter_type)
    return res

# ==================
#  Public functions
# ==================


def new(ip=None):
    """ Create new scan

    :rtype: str
    :return: scan id
    :raise: IrmaDataBaseError
    """
    with session_transaction() as session:
        # TODO get the ip
        scan = Scan(IrmaScanStatus.empty, compat.timestamp(), ip)
        scan.save(session=session)
        scanid = scan.external_id
    return scanid


def add_files(scanid, files):
    """ add file(s) to the specified scan

    :param scanid: id returned by scan_new
    :param files: dict of 'filename':str, 'data':str
    :rtype: int
    :return: int - total number of files for the scan
    :raise: IrmaDataBaseError, IrmaValueError
    """
    with session_transaction() as session:
        scan = Scan.load_from_ext_id(scanid, session)
        IrmaScanStatus.filter_status(scan.status,
                                     IrmaScanStatus.empty,
                                     IrmaScanStatus.ready)
        if scan.status == IrmaScanStatus.empty:
            # on first file added update status to 'ready'
            scan.status = IrmaScanStatus.ready
            scan.update(['status'], session=session)
            session.commit()
        for (name, data) in files.items():
            try:
                # The file exists
                file_sha256 = hashlib.sha256(data).hexdigest()
                file = File.load_from_sha256(file_sha256, session)
            except IrmaDatabaseResultNotFound:
                # It doesn't
                time = compat.timestamp()
                file = File(time, time)
                file.save(session)
                file.save_file_to_fs(data)
                file.update(session=session)
            file_web = FileWeb(file, name, scan)
            file_web.save(session)
            nb_files = len(scan.files_web)
    return nb_files


# launch operation is divided in two parts
# one is synchronous, the other called by
# a celery task is asynchronous (Ftp transfer)
def launch_synchronous(scanid, force, probelist):
    """ launch_synchronous specified scan

    :param scanid: id returned by scan_new
    :rtype: dict of 'code': int, 'msg': str [, optional 'probe_list':list]
    :return:
        on success 'probe_list' is the list of probes used for the scan
        on error 'msg' gives reason message
    :raise: IrmaDataBaseError, IrmaValueError
    """
    with session_transaction() as session:
        scan = Scan.load_from_ext_id(scanid, session)
        IrmaScanStatus.filter_status(scan.status,
                                     IrmaScanStatus.ready,
                                     IrmaScanStatus.ready)
        all_probe_list = celery_brain.probe_list()
        if probelist is not None:
            unknown_probes = []
            for p in probelist:
                if p not in all_probe_list:
                    unknown_probes.append(p)
            if len(unknown_probes) != 0:
                reason = "probe {0} unknown".format(", ".join(unknown_probes))
                raise IrmaValueError(reason)
            scan.probelist = probelist
        else:
            # all available probes
            probelist = all_probe_list

        for fw in scan.files_web:
            for p in probelist:
                # TODO probe types
                probe_result = ProbeResult(
                    0,  # TODO remove this dirty fix for probe types
                    p,
                    None,
                    IrmaProbeResultsStates.empty,
                    IrmaScanStatus.empty,
                    file_web=fw
                )
                probe_result.save(session=session)
        return probelist


def launch_asynchronous(scanid, force):
    with session_transaction() as session:
        log.info("{0}: Launching with force={1}".format(scanid, force))
        scan = Scan.load_from_ext_id(scanid, session=session)
        IrmaScanStatus.filter_status(scan.status,
                                     IrmaScanStatus.ready,
                                     IrmaScanStatus.ready)
        # Create scan request
        # dict of sha256 : probe_list
        # force parameter taken into account
        scan_request = {}
        for fw in scan.files_web:
            probes_to_do = []
            for pr in fw.probe_results:
                # init with all probes asked
                probes_to_do.append(pr.probe_name)

            log.debug("{0}: Init probe_to_do with".format(scanid,
                                                          probes_to_do))
            if not force:
                # Fetch the ref results for the file
                for rr in fw.file.ref_results:
                    log.debug("{0}: Found ref results for {1}".format(scanid,
                                                                      rr.probe_name))
                    if rr.probe_name not in probes_to_do:
                        continue
                    # if not force
                    # remove results already present
                    probes_to_do.remove(rr.probe_name)
                    # and link results to request
                    fw.probe_results.append(rr)
                fw.update(session=session)
            log.debug("{0}: Updated todo list {1}".format(scanid,
                                                          probes_to_do))

            if len(probes_to_do) > 0:
                scan_request[fw.file.sha256] = probes_to_do

        # Nothing to do
        if len(scan_request) == 0:
            scan.status = IrmaScanStatus.finished
            scan.update(['status'], session=session)
            session.commit()
            log.info("{0}: Finished nothing to do".format(scanid))
            return

        try:
            ftp_ctrl.upload_scan(scanid, scan_request.keys())
        except IrmaFtpError as e:
            log.error("{0}: Ftp upload error {1}".format(scanid, str(e)))
            scan.status = IrmaScanStatus.error_ftp_upload
            scan.update(['status'], session=session)
            return

        # launch new celery scan task on brain
        celery_brain.scan_launch(scanid, scan_request)
        scan.status = IrmaScanStatus.uploaded
        scan.update(['status'], session=session)
        log.info("{0}: Success: scan uploaded".format(scanid))
        return


def result(scanid):
    """ get results from files of specified scan

    :param scanid: id returned by scan_new
    :rtype: dict of sha256 value: dict of ['filename':str,
        'results':dict of [str probename: dict of [probe_type: str,
        status: int [, optional duration: int, optional result: int,
        optional results of probe]]]]
    :return:
        dict of results for each hash value
    :raise: IrmaDatabaseError
    """
    with session_transaction() as session:
        scan = Scan.load_from_ext_id(scanid, session=session)
        res = {}
        for fw in scan.files_web:
            probe_results = {}
            for pr in fw.probe_results:
                if pr.nosql_id is None:  # An error occurred in the process
                    probe_results[pr.probe_name] = {
                        'probe_type': pr.probe_type,
                        'status': pr.state
                    }
                else:
                    probe_results[pr.probe_name] = ProbeRealResult(
                        id=pr.nosql_id
                    ).get_results()
            res[fw.file.sha256] = {
                'filename': fw.name,
                'results': format_results(probe_results, None)
            }

        return res


def progress(scanid):
    """ get scan progress for specified scan

    :param scanid: id returned by scan_new
    :rtype: 'status': label of status [optional dict of 'total':int,
        'finished':int, 'successful':int]
    :return:
        dict with total/finished/succesful jobs submitted by irma-brain
    :raise: IrmaDatabaseError, IrmaTaskError
    """
    with session_transaction() as session:
        scan = Scan.load_from_ext_id(scanid, session=session)
        if scan.status != IrmaScanStatus.launched:
            if IrmaScanStatus.is_error(scan.status):
                raise IrmaCoreError(IrmaScanStatus.label[scan.status])
            else:
                return {'status': IrmaScanStatus.label[scan.status]}
        else:
            # Else ask brain for job status
            (retcode, res) = celery_brain.scan_progress(scanid)
            if retcode == IrmaReturnCode.success:
                s_processed = IrmaScanStatus.label[IrmaScanStatus.processed]
                if res['status'] == s_processed:
                    log.debug('{0}: Current status is {1} -> processed'.format(scanid,
                                                                               IrmaScanStatus.label[scan.status]))
                    scan.status = IrmaScanStatus.processed
                    scan.update(['status'], session=session)
                    session.commit()
                return res
            else:
                # else take directly error string from brain and
                # pass it to the caller
                raise IrmaTaskError(res)


def cancel(scanid):
    """ cancel all remaining jobs for specified scan

    :param scanid: id returned by scan_new
    :rtype: dict of 'cancel_details': total':int, 'finished':int,
        'cancelled':int
    :return:
        informations about number of cancelled jobs by irma-brain
    :raise: IrmaDatabaseError, IrmaTaskError
    """
    with session_transaction() as session:
        scan = Scan.load_from_ext_id(scanid, session=session)
        if scan.status < IrmaScanStatus.uploaded:
            # If not launched answer directly
            scan.status = IrmaScanStatus.cancelled
            scan.update(['status'], session=session)
            session.commit()
            return None
        if scan.status != IrmaScanStatus.launched:
            # If too late answer directly
            status_str = IrmaScanStatus.label[scan.status]
            if IrmaScanStatus.is_error(scan.status):
                # let the cancel finish and keep the error status
                return None
            else:
                reason = "can not cancel scan in {0} status".format(status_str)
                raise IrmaValueError(reason)

        # Else ask brain for job cancel
        (retcode, res) = celery_brain.scan_cancel(scanid)
        if retcode == IrmaReturnCode.success:
            s_processed = IrmaScanStatus.label[IrmaScanStatus.processed]
            if 'cancel_details' in res:
                scan.status = IrmaScanStatus.cancelled
                scan.update(['status'], session=session)
                return res['cancel_details']
            elif res['status'] == s_processed:
                # if scan is finished for the brain
                # it means we are just waiting for results
                scan.status = IrmaScanStatus.processed
                scan.update(['status'], session=session)
            reason = "can not cancel scan in {0} status".format(res['status'])
            raise IrmaValueError(reason)
        else:
            raise IrmaTaskError(res)


def finished(scanid):
    """ return a boolean  indicating if scan is finished
    :param scanid: id returned by scan_new
    :rtype: boolean
    :return:
        True if scan is finished
        False otherwise
    :raise: IrmaDatabaseError
    """
    with session_query() as session:
        scan = Scan.load_from_ext_id(scanid, session=session)
        return scan.finished()
