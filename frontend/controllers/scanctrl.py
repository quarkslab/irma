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
from lib.irma.common.utils import IrmaReturnCode, IrmaScanStatus, IrmaProbeType
from lib.irma.common.exceptions import IrmaCoreError, \
    IrmaDatabaseResultNotFound, IrmaValueError, IrmaTaskError, \
    IrmaFtpError
from frontend.helpers.format import IrmaFormatter
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


def new(ip):
    """ Create new scan

    :rtype: str
    :return: scan id
    :raise: IrmaDataBaseError
    """
    with session_transaction() as session:
        # TODO get the ip
        scan = Scan(compat.timestamp(), ip)
        scan.save(session=session)
        scan.set_status(IrmaScanStatus.empty, session)
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
            scan.set_status(IrmaScanStatus.ready, session)
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
            for probe_name in probelist:
                # TODO probe types
                probe_result = ProbeResult(
                    None,
                    probe_name,
                    None,
                    None,
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

            if not force:
                # Fetch the ref results for the file
                for rr in fw.file.ref_results:
                    if rr.probe_name not in probes_to_do:
                        continue
                    # if not force
                    # remove results already present
                    probes_to_do.remove(rr.probe_name)
                    # and link results to request
                    fw.probe_results.append(rr)
                fw.update(session=session)

            if len(probes_to_do) > 0:
                scan_request[fw.file.sha256] = probes_to_do

        # Nothing to do
        if len(scan_request) == 0:
            scan.set_status(IrmaScanStatus.finished, session)
            log.info("{0}: Finished nothing to do".format(scanid))
            return

        try:
            upload_list = list()
            for fw in scan.files_web:
                upload_list.append(fw.file.path)
            ftp_ctrl.upload_scan(scanid, upload_list)
        except IrmaFtpError as e:
            log.error("{0}: Ftp upload error {1}".format(scanid, str(e)))
            scan.set_status(IrmaScanStatus.error_ftp_upload, session)
            return

        # launch new celery scan task on brain
        celery_brain.scan_launch(scanid, scan_request)
        scan.set_status(IrmaScanStatus.uploaded, session)
        log.info("{0}: Success: scan uploaded".format(scanid))
        return


def result(scanid):
    """ get results from files of specified scan
        results are filtered or not according to raw parameter

    :param scanid: id returned by scan_new
    :param raw: boolean for filterting results or not
    :rtype: dict of sha256 value: dict of ['filename':str,
        'results':dict of [str probename: dict of [probe_type: str,
        status: int [, optional duration: int, optional result: int,
        optional results of probe]]]]
    :return:
        dict of results for each hash value
    :raise: IrmaDatabaseError
    """

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
    scan_res = {}

    with session_transaction() as session:
        scan = Scan.load_from_ext_id(scanid, session=session)

        scan_result_finished = 0
        scan_result_total = 0

        res = {}
        for fw in scan.files_web:
            file_results_finished = 0
            file_result_status = 0
            for pr in fw.probe_results:
                if pr.result is not None:
                    file_results_finished += 1
                    if file_result_status == 0:
                        probe_result = ProbeRealResult(id=pr.nosql_id)
                        file_result_status = probe_result.status

            scan_result_finished += file_results_finished
            scan_result_total += len(fw.probe_results)
            res[fw.id] = {
                'filename': fw.name,
                'tools_total': len(fw.probe_results),
                'tools_finished': file_results_finished,
                'status': file_result_status,
            }
        scan_res = {
            'total': scan_result_total,
            'finished': scan_result_finished,
            'status': scan.status,
            'files': res,
        }

        if scan.status != IrmaScanStatus.launched:
            if IrmaScanStatus.is_error(scan.status):
                raise IrmaCoreError(IrmaScanStatus.label[scan.status])
            else:
                return scan_res

        # Ask brain for job status
        (retcode, brain_res) = celery_brain.scan_progress(scanid)
        if retcode == IrmaReturnCode.success:
            s_processed = IrmaScanStatus.label[IrmaScanStatus.processed]
            if brain_res['status'] == s_processed and \
                scan.status != IrmaScanStatus.launched:
                # update only if status does not changed
                # during synchronous progbrain_ress task
                scan.set_status(IrmaScanStatus.processed, session)
                scan_res['status'] = scan.status
        else:
            # else take directly error string from brain and
            # pass it to the caller
            raise IrmaTaskError(brain_res)

        return scan_res


def get_result(scanid, resultid):
    with session_query() as session:
        scan = Scan.load_from_ext_id(scanid, session=session)
        file_web = session.query(FileWeb).get(resultid)

        if scan.id != file_web.scan.id:
            return

        probe_results = {}
        tools_finished = 0
        for pr in file_web.probe_results:
            if pr.result is not None:
                tools_finished += 1

                if not probe_results.has_key(pr.probe_type):
                    probe_results[pr.probe_type] = {}

                probe_res = ProbeRealResult(
                    id=pr.nosql_id
                ).get_results(raw=True)
                res = IrmaFormatter.format(pr.probe_name, probe_res)
                probe_results[pr.probe_type][pr.id] = res
        res = {
            'tools_total': len(file_web.probe_results),
            'tools_finished': tools_finished,
            'file_infos': file_web.file.to_dict(),
            'probe_results': probe_results,
        }

        res['file_infos']['name'] = file_web.name

        return res


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
            scan.set_status(IrmaScanStatus.cancelled, session)
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
                scan.set_status(IrmaScanStatus.cancelled, session)
                return res['cancel_details']
            elif res['status'] == s_processed:
                # if scan is finished for the brain
                # it means we are just waiting for results
                scan.set_status(IrmaScanStatus.processed, session)
                session.commit()
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


def set_launched(scanid):
    """ set status launched for scan
    :param scanid: id returned by scan_new
    :return: None
    :raise: IrmaDatabaseError
    """
    with session_transaction() as session:
        print("Scanid {0} is now launched".format(scanid))
        scan = Scan.load_from_ext_id(scanid, session=session)
        if scan.status == IrmaScanStatus.uploaded:
            scan.set_status(IrmaScanStatus.launched, session)


def sanitize_dict(d):
    new = {}
    for k, v in d.iteritems():
        if isinstance(v, dict):
            v = sanitize_dict(v)
        newk = k.replace('.', '_').replace('$', '')
        new[newk] = v
    return new


def set_result(scanid, file_hash, probe, result):
    with session_transaction() as session:
        scan = Scan.load_from_ext_id(scanid, session=session)
        fws = []

        for file_web in scan.files_web:
            if file_hash == file_web.file.sha256:
                fws.append(file_web)
        if len(fws) == 0:
            print ("filename not found in scan")
            return

        fws[0].file.timestamp_last_scan = compat.timestamp()
        fws[0].file.update(['timestamp_last_scan'], session=session)

        sanitized_res = sanitize_dict(result)

        # update results for all files with same sha256
        for fw in fws:
            # Update main reference results with fresh results
            pr = None
            ref_res_names = [rr.probe_name for rr in fw.file.ref_results]
            for probe_result in fw.probe_results:
                if probe_result.probe_name == probe:
                    pr = probe_result
                    if probe_result.probe_name not in ref_res_names:
                        fw.file.ref_results.append(probe_result)
                    else:
                        for rr in fw.file.ref_results:
                            if probe_result.probe_name == rr.probe_name:
                                fw.file.ref_results.remove(rr)
                                fw.file.ref_results.append(probe_result)
                                break
                    break
            fw.file.update(session=session)

            # save the handled results
            s_duration = sanitized_res.get('duration', None)
            s_type = sanitized_res.get('type', None)
            s_name = sanitized_res.get('name', None)
            s_version = sanitized_res.get('version', None)
            s_results = sanitized_res.get('results', None)
            s_status = sanitized_res.get('status', None)

            prr = ProbeRealResult(
                name=s_name,
                type=s_type,
                version=s_version,
                status=s_status,
                duration=s_duration,
                results=s_results,
                # keep a copy of raw dict in raw key
                raw=sanitized_res
            )
            pr.nosql_id = prr.id
            pr.result = s_status
            pr.probe_type = IrmaProbeType.normalize(s_type)
            pr.update(session=session)
            probedone = []
            for pr in fw.probe_results:
                if pr.nosql_id is not None:
                    probedone.append(pr.probe_name)
            print("Scanid {0}".format(scanid) +
                  "Result from {0} ".format(probe) +
                  "probedone {0}".format(probedone))

        if scan.finished():
            scan.set_status(IrmaScanStatus.finished, session)
            # launch flush celery task on brain
            celery_brain.scan_flush(scanid)


def info(scanid):
    with session_transaction() as session:
        info = {}
        scan = Scan.load_from_ext_id(scanid, session=session)
        info['ip'] = scan.ip
        info['date'] = scan.date
        info['status'] = IrmaScanStatus.label[scan.status]
        info['finished'] = scan.finished()
        info['files'] = dict()
        if len(scan.files_web) != 0:
            for file_web in scan.files_web:
                info['files'][file_web.name] = file_web.file.sha256
            # build probelist with last item of scan.files_web
            info['probelist'] = list()
            for pr in file_web.probe_results:
                info['probelist'].append(pr.probe_name)
        info['events'] = {}
        for event in scan.events:
            status = IrmaScanStatus.label[event.status]
            info['events'][status] = event.timestamp
        return info
