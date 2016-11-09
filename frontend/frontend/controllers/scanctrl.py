#
# Copyright (c) 2013-2016 Quarkslab.
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

import logging
from lib.common import compat
from lib.irma.common.utils import IrmaReturnCode, IrmaScanStatus, IrmaProbeType
from lib.irma.common.exceptions import IrmaDatabaseResultNotFound, \
    IrmaValueError, IrmaTaskError, IrmaFtpError
import frontend.controllers.braintasks as celery_brain
import frontend.controllers.ftpctrl as ftp_ctrl
from frontend.helpers.sessions import session_transaction
from frontend.models.sqlobjects import Scan, File, FileWeb, ProbeResult
from lib.common.mimetypes import Magic
from lib.irma.common.utils import IrmaScanRequest
from frontend.controllers import braintasks
import ntpath
from lib.common.utils import save_to_file
from lib.common.hash import sha256sum, sha1sum, md5sum
from frontend.helpers.utils import build_sha256_path
from fasteners import interprocess_locked
from config.parser import get_lock_path

log = logging.getLogger(__name__)
interprocess_lock_path = get_lock_path()

# ===================
#  Internals helpers
# ===================


def _new_file(fileobj, session):
    sha256 = sha256sum(fileobj)
    # split files between subdirs
    path = build_sha256_path(sha256)
    try:
        # The file exists
        log.debug("try opening file with sha256: %s", sha256)
        file = File.load_from_sha256(sha256, session)
        if file.path is None:
            log.debug("file sample missing writing it")
            save_to_file(fileobj, path)
            file.path = path
    except IrmaDatabaseResultNotFound:
        # It doesn't
        time = compat.timestamp()
        sha1 = sha1sum(fileobj)
        md5 = md5sum(fileobj)
        # determine file mimetype
        magic = Magic()
        # magic only deal with buffer
        # feed it with a 4MB buffer
        mimetype = magic.from_buffer(fileobj.read(2 ** 22))
        size = save_to_file(fileobj, path)
        log.debug("not present, saving, sha256 %s sha1 %s"
                  "md5 %s size %s mimetype: %s",
                  sha256, sha1, md5, size, mimetype)
        file = File(sha256, sha1, md5, size, mimetype, path, time, time)
        session.add(file)
    return file


def _new_fileweb(scan, filename, fileobj, session):
    log.debug("filename: %s", filename)
    file = _new_file(fileobj, session)
    (path, name) = ntpath.split(filename)
    file_web = FileWeb(file, name, path, scan)
    session.add(file_web)
    session.commit()
    return file_web


def _add_empty_result(fw, probelist, scan, session):
    log.debug("fw: %s", fw.name)
    scan_known_results = _fetch_known_results(fw.file, scan, session)
    updated_probelist = []
    for probe_name in probelist:
        # Fetch the ref results for the file
        ref_results = filter(lambda x: x.name == probe_name,
                             fw.file.ref_results)
        # Fetch the already produced result in the current scan
        scan_results = filter(lambda x: x.name == probe_name,
                              scan_known_results)
        if len(ref_results) == 1 and not scan.force:
            # we ask for results already present
            # and we found one use it
            probe_result = ref_results[0]
            fw.probe_results.append(probe_result)
            log.debug("link refresult for %s probe %s",
                      fw.name,
                      probe_name)
        elif scan.force and len(scan_results) == 1:
            # We ask for a new analysis
            # but there is already one in current scan
            # just link it
            log.debug("link scanresult for %s probe %s",
                      fw.name,
                      probe_name)
            probe_result = scan_results[0]
            fw.probe_results.append(probe_result)
        else:
            # results is not known or analysis is forced
            # create empty result
            # TODO probe types
            log.debug("creating empty result for %s probe %s",
                      fw.name,
                      probe_name)
            probe_result = ProbeResult(
                None,
                probe_name,
                None,
                None,
                file_web=fw
            )
            # A job scan should be sent
            # let the probe in scan_request
            updated_probelist.append(probe_name)
            session.add(probe_result)
            session.commit()
    return updated_probelist


def _fetch_known_results(file, scan, session):
    scan_known_result = []
    known_fw_list = FileWeb.load_by_scanid_fileid(scan.id, file.id, session)
    if known_fw_list is not None and len(known_fw_list) > 1:
        log.debug("found %d file in current scan",
                  len(known_fw_list))
        scan_known_result = known_fw_list[0].probe_results
        log.debug("%d known results",
                  len(scan_known_result))
    return scan_known_result


def _add_empty_results(fw_list, scan_request, scan, session):
    log.debug("scanid : %s scan_request: %s", scan.external_id,
              scan_request.to_dict())
    new_scan_request = IrmaScanRequest()
    for fw in fw_list:
        probelist = scan_request.get_probelist(fw.file.sha256)
        updated_probe_list = _add_empty_result(fw, probelist, scan, session)
        # Update scan_request according to results already known linked
        # in _add_empty_result
        if len(updated_probe_list) > 0:
            filehash = fw.file.sha256
            mimetype = scan_request.get_mimetype(filehash)
            log.debug("Update scan_request for file %s"
                      "previously asked %s now %s",
                      filehash, scan_request.get_probelist(filehash),
                      updated_probe_list)
            new_scan_request.add_file(filehash,
                                      updated_probe_list,
                                      mimetype)
    log.debug("new scan_request %s", new_scan_request.to_dict())
    return new_scan_request


def _create_scan_request(fw_list, probelist, mimetype_filtering):
    # Create scan request
    # dict of sha256 : probe_list
    # force parameter taken into account
    log.debug("probelist: %s mimetype_filtering: %s",
              probelist, mimetype_filtering)
    scan_request = IrmaScanRequest()
    for fw in fw_list:
        scan_request.add_file(fw.file.sha256,
                              probelist,
                              fw.file.mimetype)
    if mimetype_filtering is True:
        srdict = scan_request.to_dict()
        filtered_srdict = braintasks.mimetype_filter_scan_request(srdict)
        scan_request = IrmaScanRequest(filtered_srdict)
    return scan_request


def _sanitize_res(d):
    if isinstance(d, unicode):
        # Fix for JSONB
        return d.replace("\u0000", "").replace(u"\x00", "")
    elif isinstance(d, list):
        return [_sanitize_res(x) for x in d]
    elif isinstance(d, dict):
        new = {}
        for k, v in d.iteritems():
            newk = k.replace('.', '_').replace('$', '')
            new[newk] = _sanitize_res(v)
        return new
    else:
        return d


def _append_new_files_to_scan(scan, uploaded_files, session):
    new_fws = []
    for (file_name, file_sha256) in uploaded_files.items():
        file_obj = ftp_ctrl.download_file_data(scan.external_id, file_sha256)
        fw = _new_fileweb(scan, file_name, file_obj, session)
        file_obj.close()
        log.debug("scan %s: new fileweb id %s for file %s",
                  scan.external_id, fw.external_id, fw.name)
        new_fws.append(fw)
    return new_fws


def _resubmit_files(scan, parent_file, resubmit_fws, hash_uploaded, session):
    fws = parent_file.files_web
    if len(fws) == 0:
        log.error("file %s not found in scan", parent_file.sha256)
        return
    fws_filtered = []
    for fw in resubmit_fws:
        # Either fw is already in scan and duplicate result
        if fw.file.sha256 in hash_uploaded:
            # grab probelist from filewebs linked to the same file
            # in current scan
            probelist = [p.name for p in _fetch_known_results(fw.file,
                                                              scan, session)]
            # and add link to their results
            _add_empty_result(fw, probelist, scan, session)
        else:
            # if new to scan, build a new one
            # (done later in _add_empty_results)
            fws_filtered.append(fw)

    log.debug("scan %s: %d new files to resubmit",
              scan.external_id, len(fws_filtered))
    if len(fws_filtered) != 0:
        scan_request = _create_scan_request(fws_filtered,
                                            scan.get_probelist(),
                                            scan.mimetype_filtering)
        scan_request = _add_empty_results(fws_filtered, scan_request,
                                          scan, session)
        celery_brain.scan_launch(scan.external_id, scan_request.to_dict())
    return


def _fetch_probe_result(fw, probe):
    pr_list = filter(lambda x: x.name == probe, fw.probe_results)
    if len(pr_list) > 1:
        log.error("Integrity error: multiple results for "
                  "file {0} probe {1}".format(fw.name, probe))
    elif len(pr_list) == 0:
        log.warning("No result created for "
                    "file {0} probe {1}".format(fw.name, probe))
        return None
    return pr_list[0]


def _update_ref_results(fw, file, pr):
    rr_list = filter(lambda x: x.name == pr.name, file.ref_results)
    if len(rr_list) == 0:
        # current probe is not part of ref results
        # just add it
        file.ref_results.append(pr)
    elif len(rr_list) == 1:
        # a reference result already exist
        # replace it
        file.ref_results.remove(rr_list[0])
        file.ref_results.append(pr)
    else:
        log.error("Integrity error: multiple refresults for "
                  "file {0} probe {1}".format(file.sha256, pr.name))
    return


def _filter_children(scan, parent_file, uploaded_files):
    # filter FileWeb already linked to this parent in the current scan
    children_fw = [fw for fw in parent_file.children
                   if fw in scan.files_web]
    log.debug("for parent %s current children in scan: %s",
              parent_file.sha256,
              " - ".join([c.name for c in children_fw]))
    uploaded_files_filtered = dict()
    for (file_name, file_sha256) in uploaded_files.items():
        fw = filter(lambda x: x.name == file_name and
                    x.file.sha256 == file_sha256,
                    children_fw)
        if len(fw) == 0:
            uploaded_files_filtered.update({file_name: file_sha256})
    return uploaded_files_filtered


# ================
#  Public methods
# ================


def add_files(scan, files, session):
    """ add file(s) to the specified scan

    :param scanid: id returned by scan_new
    :param files: dict of {filename, file-obj}
    :rtype: int
    :return: int - total number of files for the scan
    :raise: IrmaDataBaseError, IrmaValueError
    """
    log.debug("scanid: %s", scan.external_id)
    IrmaScanStatus.filter_status(scan.status,
                                 IrmaScanStatus.empty,
                                 IrmaScanStatus.ready)
    if scan.status == IrmaScanStatus.empty:
        # on first file added update status to 'ready'
        scan.set_status(IrmaScanStatus.ready)

    for (filename, data) in files.items():
        # Using ntpath.split as it handles
        # windows path and Linux path
        log.debug("filename: %s", filename)
        _new_fileweb(scan, filename, data, session)
    session.commit()


# launch operation is divided in two parts
# one is synchronous, the other called by
# a celery task is asynchronous (Ftp transfer)
def check_probe(scan, probelist, session):
    """ check_probe specified scan

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
    else:
        probelist = all_probe_list
    log.debug("scanid: %s probelist: %s", scan.external_id, probelist)
    scan.set_probelist(probelist)
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
    log.debug("scanid: %s", scan.external_id)
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


# Used by tasks.py, second part of the scan launch operation
def launch_asynchronous(scanid):
    log.debug("scanid: %s", scanid)
    with session_transaction() as session:
        scan = Scan.load_from_ext_id(scanid, session=session)
        IrmaScanStatus.filter_status(scan.status,
                                     IrmaScanStatus.ready,
                                     IrmaScanStatus.ready)
        scan_request = _create_scan_request(scan.files_web,
                                            scan.get_probelist(),
                                            scan.mimetype_filtering)
        scan_request = _add_empty_results(scan.files_web, scan_request,
                                          scan, session)
        # Nothing to do
        if scan_request.nb_files == 0:
            scan.set_status(IrmaScanStatus.finished)
            session.commit()
            log.warning("scanid: %s finished nothing to do", scanid)
            return

        try:
            upload_list = list()
            for file in scan.files:
                upload_list.append(file.path)
            ftp_ctrl.upload_scan(scanid, upload_list)
        except IrmaFtpError as e:
            log.error("scanid: %s ftp upload error %s", scanid, str(e))
            scan.set_status(IrmaScanStatus.error_ftp_upload)
            session.commit()
            return

        # launch new celery scan task on brain
        celery_brain.scan_launch(scanid, scan_request.to_dict())
        scan.set_status(IrmaScanStatus.uploaded)
        session.commit()
        log.info("scanid: %s uploaded", scanid)
        return


def set_launched(scanid, scan_report_dict):
    """ set status launched for scan
    :param scanid: id returned by scan_new
    :param scanreport: scan details output by brain
    :return: None
    :raise: IrmaDatabaseError
    """
    with session_transaction() as session:
        log.info("scanid: %s is now launched", format(scanid))
        scan = Scan.load_from_ext_id(scanid, session=session)
        if scan.status == IrmaScanStatus.uploaded:
            scan.set_status(IrmaScanStatus.launched)
            session.commit()


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
        sanitized_res = _sanitize_res(result)

        # update results for all files with same sha256
        for fw in fws:
            # Update main reference results with fresh results
            pr = _fetch_probe_result(fw, probe)
            if pr is None:
                continue
            _update_ref_results(fw, fw.file, pr)
            fw.file.update(session=session)
            # fill ProbeResult with probe raw results
            pr.doc = sanitized_res
            pr.status = sanitized_res.get('status', None)
            s_type = sanitized_res.get('type', None)
            pr.type = IrmaProbeType.normalize(s_type)
            pr.update(session=session)
            probedone = []
            for fw_pr in fw.probe_results:
                if fw_pr.doc is not None:
                    probedone.append(fw_pr.name)
            log.info("scanid: %s result from %s probedone %s",
                     scanid, probe, probedone)
    is_finished(scanid)


# insure there is only one call running at a time
# among the different workers
@interprocess_locked(interprocess_lock_path)
def is_finished(scanid):
    with session_transaction() as session:
        scan = Scan.load_from_ext_id(scanid, session=session)
        if scan.finished() and scan.status != IrmaScanStatus.finished:
            scan.set_status(IrmaScanStatus.finished)
            session.commit()
            # launch flush celery task on brain
            log.debug("scanid: %s calling scan_flush", scan.external_id)
            celery_brain.scan_flush(scan.external_id)


def handle_output_files(scanid, parent_file_hash, probe, result):
    with session_transaction() as session:
        scan = Scan.load_from_ext_id(scanid, session=session)
        uploaded_files = result.get('uploaded_files', None)
        if uploaded_files is None or not scan.resubmit_files:
            log.debug("scanid: %s Nothing to resubmit or resubmit disabled",
                      scanid)
            return
        # check whether the results was already received or not
        log.debug("scanid: %s checking if results already received",
                  scanid)
        parent_file = File.load_from_sha256(parent_file_hash, session)
        uploaded_files = _filter_children(scan, parent_file, uploaded_files)
        if len(uploaded_files) == 0:
            log.info("scanid: %s no new uploaded files continue", scanid)
            return
        # filter already present file in current scan
        log.info("scanid: %s appending new uploaded files %s",
                 scanid, uploaded_files.keys())
        hash_uploaded = [f.sha256 for f in scan.files]
        new_fws = _append_new_files_to_scan(scan, uploaded_files, session)
        for fw in new_fws:
            parent_file.children.append(fw)
        _resubmit_files(scan, parent_file, new_fws, hash_uploaded, session)
