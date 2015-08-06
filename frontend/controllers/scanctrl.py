#
# Copyright (c) 2013-2015 QuarksLab.
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
from lib.common import compat
from lib.irma.common.utils import IrmaReturnCode, IrmaScanStatus, IrmaProbeType
from lib.irma.common.exceptions import IrmaDatabaseResultNotFound, \
    IrmaValueError, IrmaTaskError, IrmaFtpError
import frontend.controllers.braintasks as celery_brain
import frontend.controllers.ftpctrl as ftp_ctrl
from frontend.helpers.sessions import session_transaction
from frontend.models.nosqlobjects import ProbeRealResult
from frontend.models.sqlobjects import Scan, File, FileWeb, ProbeResult


log = logging.getLogger()


def _new_file(data, session):
    try:
        # The file exists
        file_sha256 = hashlib.sha256(data).hexdigest()
        file = File.load_from_sha256(file_sha256, session, data)
    except IrmaDatabaseResultNotFound:
        # It doesn't
        time = compat.timestamp()
        file = File(time, time)
        file.save_file_to_fs(data)
        session.add(file)
    return file


def _new_fileweb(scan, name, data, session):
    file = _new_file(data, session)
    file_web = FileWeb(file, name, scan, len(scan.files_web))
    session.add(file_web)
    return file_web


def add_files(scan, files, session):
    """ add file(s) to the specified scan

    :param scanid: id returned by scan_new
    :param files: dict of 'filename':str, 'data':str
    :rtype: int
    :return: int - total number of files for the scan
    :raise: IrmaDataBaseError, IrmaValueError
    """
    IrmaScanStatus.filter_status(scan.status,
                                 IrmaScanStatus.empty,
                                 IrmaScanStatus.ready)
    if scan.status == IrmaScanStatus.empty:
        # on first file added update status to 'ready'
        scan.set_status(IrmaScanStatus.ready)

    for (name, data) in files.items():
        _new_fileweb(scan, name, data, session)
    session.commit()


def _add_empty_result(fw_list, probe_list, scan, session):
    log.debug("add_empty results for %d filewebs",
              len(fw_list))
    for fw in fw_list:
        known_fw_list = filter(lambda x: x.file.sha256 == fw.file.sha256,
                               scan.files_web)
        scan_known_result = []
        log.debug("add_empty_results: Found %d file in current scan",
                  len(known_fw_list))
        if len(known_fw_list) >= 1:
            scan_known_result = known_fw_list[0].probe_results
            log.debug("add_empty_results: %d known results",
                      len(scan_known_result))
        for probe_name in probe_list:
            # Fetch the ref results for the file
            ref_results = filter(lambda x: x.name == probe_name,
                                 fw.file.ref_results)
            # Fetch the already produced result in the current scan
            scan_results = filter(lambda x: x.name == probe_name,
                                  scan_known_result)
            if len(ref_results) == 1 and not scan.force:
                # we ask for results already present
                # and we found one use it
                probe_result = ref_results[0]
                fw.probe_results.append(probe_result)
            elif scan.force and len(scan_results) == 1:
                # We ask for a new analysis
                # but there is already one in current scan
                # just link it
                probe_result = scan_results[0]
                fw.probe_results.append(probe_result)
            else:
                # results is not known or analysis is forced
                # create empty result
                # TODO probe types
                probe_result = ProbeResult(
                    None,
                    probe_name,
                    None,
                    None,
                    file_web=fw
                )
                session.add(probe_result)


# launch operation is divided in two parts
# one is synchronous, the other called by
# a celery task is asynchronous (Ftp transfer)
def launch_synchronous(scan, probelist, session):
    """ launch_synchronous specified scan

    :param scanid: id returned by scan_new
    :rtype: dict of 'code': int, 'msg': str [, optional 'probe_list':list]
    :return:
        on success 'probe_list' is the list of probes used for the scan
        on error 'msg' gives reason message
    :raise: IrmaDataBaseError, IrmaValueError
    """
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
    _add_empty_result(scan.files_web, probelist, scan, session)
    session.commit()


def cancel(scan, session):
    """ cancel all remaining jobs for specified scan

    :param scanid: id returned by scan_new
    :rtype: dict of 'cancel_details': total':int, 'finished':int,
        'cancelled':int
    :return:
        informations about number of cancelled jobs by irma-brain
    :raise: IrmaDatabaseError, IrmaTaskError
    """
    if scan.status < IrmaScanStatus.uploaded:
        # If not launched answer directly
        scan.set_status(IrmaScanStatus.cancelled)
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
    (retcode, res) = celery_brain.scan_cancel(scan.external_id)
    if retcode == IrmaReturnCode.success:
        s_processed = IrmaScanStatus.label[IrmaScanStatus.processed]
        if 'cancel_details' in res:
            scan.set_status(IrmaScanStatus.cancelled)
            session.commit()
            return res['cancel_details']
        elif res['status'] == s_processed:
            # if scan is finished for the brain
            # it means we are just waiting for results
            scan.set_status(IrmaScanStatus.processed)
            session.commit()
        reason = "can not cancel scan in {0} status".format(res['status'])
        raise IrmaValueError(reason)
    else:
        raise IrmaTaskError(res)


def create_scan_request(fw_list):
    # Create scan request
    # dict of sha256 : probe_list
    # force parameter taken into account
    scan_request = {}
    for fw in fw_list:
        probes_to_do = []
        for pr in fw.probe_results:
            # init with all probes asked not already present
            if pr.nosql_id is None:
                probes_to_do.append(pr.name)
        if len(probes_to_do) > 0:
            scan_request[fw.file.sha256] = probes_to_do
    return scan_request


# Used by tasks.py
def launch_asynchronous(scanid):
    with session_transaction() as session:
        log.info("{0}: Launching asynchronously".format(scanid))
        scan = Scan.load_from_ext_id(scanid, session=session)
        IrmaScanStatus.filter_status(scan.status,
                                     IrmaScanStatus.ready,
                                     IrmaScanStatus.ready)
        scan_request = create_scan_request(scan.files_web)

        # Nothing to do
        if len(scan_request) == 0:
            scan.set_status(IrmaScanStatus.finished)
            session.commit()
            log.info("{0}: Finished nothing to do".format(scanid))
            return

        try:
            upload_list = list()
            for fw in scan.files_web:
                upload_list.append(fw.file.path)
            ftp_ctrl.upload_scan(scanid, upload_list)
        except IrmaFtpError as e:
            log.error("{0}: Ftp upload error {1}".format(scanid, str(e)))
            scan.set_status(IrmaScanStatus.error_ftp_upload)
            session.commit()
            return

        # launch new celery scan task on brain
        celery_brain.scan_launch(scanid, scan_request)
        scan.set_status(IrmaScanStatus.uploaded)
        session.commit()
        log.info("{0}: Success: scan uploaded".format(scanid))
        return


def set_launched(scanid):
    """ set status launched for scan
    :param scanid: id returned by scan_new
    :return: None
    :raise: IrmaDatabaseError
    """
    with session_transaction() as session:
        log.info("Scanid %s is now launched", format(scanid))
        scan = Scan.load_from_ext_id(scanid, session=session)
        if scan.status == IrmaScanStatus.uploaded:
            scan.set_status(IrmaScanStatus.launched)
            session.commit()


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
        fws = scan.get_filewebs_by_sha256(file_hash)
        if len(fws) == 0:
            log.error("file %s not found in scan", file_hash)
            return

        fws_file = File.load_from_sha256(file_hash, session)
        fws_file.timestamp_last_scan = compat.timestamp()
        fws_file.update(['timestamp_last_scan'], session=session)
        sanitized_res = sanitize_dict(result)

        # update results for all files with same sha256
        for fw in fws:
            # Update main reference results with fresh results
            pr = None
            ref_res_names = [rr.name for rr in fw.file.ref_results]
            for probe_result in fw.probe_results:
                if probe_result.name == probe:
                    pr = probe_result
                    if probe_result.name not in ref_res_names:
                        fw.file.ref_results.append(probe_result)
                    else:
                        for rr in fw.file.ref_results:
                            if probe_result.name == rr.name:
                                fw.file.ref_results.remove(rr)
                                fw.file.ref_results.append(probe_result)
                                break
                    break
            fw.file.update(session=session)

            # init empty NoSql record to get
            # all mandatory fields initialized
            prr = ProbeRealResult()
            # and fill with probe raw results
            prr.update(sanitized_res)
            # link it to Sql record
            pr.nosql_id = prr.id
            pr.status = sanitized_res.get('status', None)
            s_type = sanitized_res.get('type', None)
            pr.type = IrmaProbeType.normalize(s_type)
            pr.update(session=session)
            probedone = []
            for pr in fw.probe_results:
                if pr.nosql_id is not None:
                    probedone.append(pr.name)
            log.info("Scanid %s result from %s probedone %s",
                     scanid, probe, probedone)

        if scan.finished():
            scan.set_status(IrmaScanStatus.finished)
            session.commit()
            # launch flush celery task on brain
            celery_brain.scan_flush(scanid)


def _append_new_files_to_scan(scan, uploaded_files, session):
    new_fws = []
    for (file_name, file_sha256) in uploaded_files.items():
        file_data = ftp_ctrl.download_file_data(scan.external_id, file_sha256)
        new_fws.append(_new_fileweb(scan, file_name, file_data, session))
    return new_fws


def _resubmit_files(scan, parent_file, resubmit_fws, hash_uploaded, session):
    fws = parent_file.files_web
    if len(fws) == 0:
        log.error("file %s not found in scan", parent_file.sha256)
        return
    probe_requested = [pr.name for pr in fws[0].probe_results]
    # Now create an emtpy result for each resubmit_fw with same probelist
    # as their parent
    _add_empty_result(resubmit_fws, probe_requested, scan, session)
    # TODO add current available results

    # Now filter fws that have already a file uploaded in the current scan
    fws_filtered = filter(lambda x: x.file.sha256 not in hash_uploaded,
                          resubmit_fws)
    log.info("Scan %s: %d new files to resubmit",
             scan.external_id, len(fws_filtered))
    if len(fws_filtered) != 0:
        scan_request = create_scan_request(fws_filtered)
        celery_brain.scan_launch(scan.external_id, scan_request)
    return


def handle_output_files(scanid, parent_file_hash, probe, result):
    uploaded_files = result.get('uploaded_files', None)
    # TODO resubmit switch
    resubmit = True
    if uploaded_files is None or not resubmit:
        return
    with session_transaction() as session:
        log.info("Scanid %s: Appending new uploaded files %s",
                 scanid, uploaded_files.keys())
        scan = Scan.load_from_ext_id(scanid, session=session)
        parent_file = File.load_from_sha256(parent_file_hash, session)
        # filter already present file in current scan
        hash_uploaded = [f.sha256 for f in scan.files]
        new_fws = _append_new_files_to_scan(scan, uploaded_files, session)
        for fw in new_fws:
            parent_file.children.append(fw)
        _resubmit_files(scan, parent_file, new_fws, hash_uploaded, session)
