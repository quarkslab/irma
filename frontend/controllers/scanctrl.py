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
    IrmaProbeResultsStates, IrmaScanResults
from lib.irma.common.exceptions import IrmaDatabaseError, \
    IrmaDatabaseResultNotFound, IrmaValueError, IrmaTaskError
from frontend.format import IrmaFormatter
from frontend.helpers.sql import session_transaction, session_query
import frontend.controllers.braintasks as celery_brain
import frontend.controllers.frontendtasks as celery_frontend


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
        res = filter(lambda x:
                     'category' in x and x['category'] in filter_type,
                     res)
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
        scan = Scan(IrmaScanStatus.created, compat.timestamp(), ip)
        scan.save(session=session)
        scanid = scan.external_id
    return scanid


def add_files(scanid, files):
    """ add file(s) to the specified scan

    :param scanid: id returned by scan_new
    :param files: dict of 'filename':str, 'data':str
    :rtype: int
    :return: int - total number of files for the scan
    :raise: IrmaWarning If the scan has already been started
    """
    with session_transaction() as session:
        scan = Scan.load_from_ext_id(scanid, session)
        if scan.status != IrmaScanStatus.created:
            # Cannot add file to a launched scan
            status_str = IrmaScanStatus.label[scan.status]
            msg = "Can't add file to a scan {0}".format(status_str)
            raise IrmaValueError(msg)
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


def launch(scanid, force, probelist):
    """ launch specified scan

    :param scanid: id returned by scan_new
    :rtype: dict of 'code': int, 'msg': str [, optional 'probe_list':list]
    :return:
        on success 'probe_list' is the list of probes used for the scan
        on error 'msg' gives reason message
    :raise: IrmaWarning, IrmaTaskError
    """
    with session_transaction() as session:
        scan = Scan.load_from_ext_id(scanid, session)
        if scan.status != IrmaScanStatus.created:
            # Cannot launch scan with other status
            raise IrmaValueError(IrmaScanStatus.label[scan.status])
        all_probe_list = probe_list()
        if len(all_probe_list) == 0:
            scan.status = IrmaScanStatus.finished
            scan.update(['status'], session=session)
            session.commit()
            raise IrmaTaskError("No probe available")

        if probelist is not None:
            unknown_probes = []
            for p in probelist:
                if p not in all_probe_list:
                    unknown_probes.append(p)
            if len(unknown_probes) != 0:
                reason = "Probe {0} unknown".format(", ".join(unknown_probes))
                scan.status = IrmaScanStatus.finished
                scan.update(['status'], session=session)
                session.commit()
                raise IrmaTaskError(reason)
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
                    IrmaProbeResultsStates.created,
                    IrmaScanStatus.created,
                    file_web=fw
                )
                probe_result.save(session=session)
        # launch scan via frontend task
        celery_frontend.scan_launch(scanid, force)
        return probelist


def result(scanid):
    """ get results from files of specified scan

    :param scanid: id returned by scan_new
    :rtype: dict of sha256 value: dict of ['filename':str,
        'results':dict of [str probename: dict of [probe_type: str,
        status: int [, optional duration: int, optional result: int,
        optional results of probe]]]]
    :return:
        dict of results for each hash value
    :raise: IrmaDataBaseError
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
    :rtype: dict of 'total':int, 'finished':int, 'successful':int
    :return:
        dict with total/finished/succesful jobs submitted by irma-brain
    :raise: IrmaDatabaseError, IrmaWarning, IrmaTaskError
    """
    with session_transaction() as session:
        scan = Scan.load_from_ext_id(scanid, session=session)
        if IrmaScanStatus.is_error(scan.status):
            raise IrmaTaskError(IrmaScanStatus.label[scan.status])
        elif scan.status != IrmaScanStatus.launched:
            # If not launched answer directly
            raise IrmaValueError(IrmaScanStatus.label[scan.status])
        # Else ask brain for job status
        (status, res) = celery_brain.scan_progress(scanid)
        if status == IrmaReturnCode.success:
            return res
        elif status == IrmaReturnCode.warning:
            # FIXME in task that gets results on brain
            # send a processed status to frontend
            # if scan is processed for the brain,
            # it means all probes jobs are completed
            # we are just waiting for results
            if res == IrmaScanStatus.processed:
                scan.status = IrmaScanStatus.processed
                scan.update(['status'], session=session)
                session.commit()
            raise IrmaValueError(IrmaScanStatus.label[res])
        else:
            raise IrmaTaskError(res)


def cancel(scanid):
    """ cancel all remaining jobs for specified scan

    :param scanid: id returned by scan_new
    :rtype: dict of 'cancel_details': total':int, 'finished':int,
        'cancelled':int
    :return:
        informations about number of cancelled jobs by irma-brain
    :raise: IrmaDatabaseError, IrmaWarning, IrmaTaskError
    """
    with session_transaction() as session:
        scan = Scan.load_from_ext_id(scanid, session=session)
        if scan.status != IrmaScanStatus.launched:
            # If not launched answer directly
            # Else ask brain for job status
            scan.status = IrmaScanStatus.cancelled
            scan.update(['status'], session=session)
            raise IrmaValueError(IrmaScanStatus.label[scan.status])

        (status, res) = celery_brain.scan_cancel(scanid)
        if status == IrmaReturnCode.success:
            scan.status = IrmaScanStatus.cancelled
            scan.update(['status'], session=session)
            return res
        elif status == IrmaReturnCode.warning:
            # if scan is finished for the brain
            # it means we are just waiting for results
            if res == IrmaScanStatus.processed:
                scan.status = IrmaScanStatus.processed
                scan.update(['status'], session=session)
            raise IrmaValueError(IrmaScanStatus.label[res])
        else:
            raise IrmaTaskError(res)


def finished(scanid):
    """ return a boolean  indicating if scan is finished
    :param scanid: id returned by scan_new
    :rtype: boolean
    :return:
        True if scan is finished
        False otherwise
    :raise: IrmaDatabaseError, IrmaWarning, IrmaTaskError
    """
    with session_query() as session:
        scan = Scan.load_from_ext_id(scanid, session=session)
        return scan.finished()


def probe_list():
    """ get active probe list

    :rtype: list of str
    :return:
        list of probes names
    :raise: IrmaWarning, IrmaTaskError
    """
    (status, res) = celery_brain.probe_list()
    if status == IrmaReturnCode.success:
        return res
    else:
        raise IrmaTaskError(res)

