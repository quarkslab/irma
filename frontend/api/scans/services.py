#
# Copyright (c) 2013-2018 Quarkslab.
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

from fasteners import interprocess_locked
from sqlalchemy import inspect
from api.common.sessions import session_transaction, session_query

import api.common.ftp as ftp_ctrl
import api.tasks.braintasks as celery_brain
from api.files.models import File
from api.files_ext.models import FileExt, FileProbeResult
from api.probe_results.models import ProbeResult
from api.scans.models import Scan
from config.parser import get_lock_path, get_max_resubmit_level
from irma.common.base.exceptions import IrmaValueError, IrmaTaskError
from irma.common.base.utils import IrmaReturnCode, IrmaScanStatus
from irma.common.base.utils import IrmaScanRequest

log = logging.getLogger(__name__)
interprocess_lock_path = get_lock_path()
CSV_SEPARATOR = ";"

# ===================
#  Internals helpers
# ===================


def _add_empty_result(file_ext, probelist, scan, session):
    log.debug("scan %s: file %s add empty results",
              scan.external_id, file_ext.external_id)
    updated_probelist = []
    for probe_name in probelist:
        # Fetch the ref results for the file
        ref_result = file_ext.file.get_ref_result(probe_name)
        if ref_result is not None and not scan.force:
            # we ask for results already present
            # and we found one use it
            file_ext.probe_results.append(ref_result)
            log.debug("scan %s: link refresult for %s probe %s",
                      scan.external_id,
                      file_ext.external_id,
                      probe_name)
        else:
            # results is not known or analysis is forced
            # create empty result
            # TODO probe types
            log.debug("scan %s: creating empty result for %s probe %s",
                      scan.external_id,
                      file_ext.external_id,
                      probe_name)
            probe_result = ProbeResult(
                None,
                probe_name,
                None,
                None,
                files_ext=file_ext
            )
            # A job scan should be sent
            # let the probe in scan_request
            updated_probelist.append(probe_name)
            session.add(probe_result)
            session.commit()
    return updated_probelist


def _add_empty_results(file_ext_list, scan_request, scan, session):
    log.debug("scan %s: scan_request: %s", scan.external_id,
              scan_request.to_dict())
    new_scan_request = IrmaScanRequest()
    for file_ext in file_ext_list:
        probelist = scan_request.get_probelist(file_ext.external_id)
        updated_probe_list = _add_empty_result(file_ext, probelist,
                                               scan, session)
        # Update scan_request according to results already known linked
        # in _add_empty_result
        if len(updated_probe_list) > 0:
            mimetype = scan_request.get_mimetype(file_ext.external_id)
            log.debug("scan %s: update scan_request for file %s"
                      "previously asked %s now %s",
                      scan.external_id, file_ext.external_id,
                      scan_request.get_probelist(file_ext.external_id),
                      updated_probe_list)
            new_scan_request.add_file(file_ext.external_id,
                                      updated_probe_list,
                                      mimetype)
    log.debug("scan %s: new scan_request %s",
              scan.external_id, new_scan_request.to_dict())
    return new_scan_request


def _create_scan_request(file_ext_list, probelist, mimetype_filtering):
    # Create scan request
    # dict of filename : probe_list
    # force parameter taken into account
    log.debug("probelist: %s mimetype_filtering: %s",
              probelist, mimetype_filtering)
    scan_request = IrmaScanRequest()
    for file_ext in file_ext_list:
        scan_request.add_file(file_ext.external_id,
                              probelist,
                              file_ext.file.mimetype)
    if mimetype_filtering is True:
        srdict = scan_request.to_dict()
        filtered_srdict = celery_brain.mimetype_filter_scan_request(srdict)
        scan_request = IrmaScanRequest(filtered_srdict)
    return scan_request


def _sanitize_res(d):
    if isinstance(d, str):
        # Fix for JSONB
        return d.replace("\u0000", "").replace("\x00", "")
    elif isinstance(d, list):
        return [_sanitize_res(x) for x in d]
    elif isinstance(d, dict):
        new = {}
        for k, v in d.items():
            newk = k.replace('.', '_').replace('$', '')
            new[newk] = _sanitize_res(v)
        return new
    else:
        return d


def _get_or_create_new_files(uploaded_files, session):
    new_files = {}
    for file_tmp_id in uploaded_files:
        file_obj = ftp_ctrl.download_file_data(file_tmp_id)
        file = File.get_or_create(file_obj, session)
        file_obj.close()
        new_files[file_tmp_id] = file
    return new_files


def _append_new_files_to_scan(scan, uploaded_files, probe_result, depth):
    new_files_ext = []
    session = inspect(scan).session
    # Do it in two times for allowing retries
    # First create all new files then rename temp name on brain
    # to file_id name
    new_files = _get_or_create_new_files(uploaded_files.values(), session)
    for (file_realname, file_tmp_id) in uploaded_files.items():
        file = new_files[file_tmp_id]
        file_ext = FileProbeResult(file, file_realname, probe_result, depth)
        file_ext.scan = scan
        session.add(file_ext)
        session.commit()
        log.debug("scan %s: new file_ext id %s for file %s",
                  scan.external_id, file_ext.external_id, file_ext.name)

        ftp_ctrl.rename_file(file_tmp_id, file_ext.external_id)
        new_files_ext.append(file_ext)
    return new_files_ext


# ================
#  Public methods
# ================


def cancel(scan, session):
    """ cancel all remaining jobs for specified scan

    :param scan_id: id returned by scan_new
    :rtype: dict of 'cancel_details': total':int, 'finished':int,
        'cancelled':int
    :return:
        informations about number of cancelled jobs by irma-brain
    :raise: IrmaDatabaseError, IrmaTaskError
    """
    log.debug("scan %s: cancel", scan.external_id)
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
            log.error("scan %s: %s", scan.external_id, reason)
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
        log.error("scan %s: %s", scan.external_id, reason)
        raise IrmaValueError(reason)
    else:
        raise IrmaTaskError(res)


def set_result(file_ext_id, probe, result):
    with session_transaction() as session:
        file_ext = FileExt.load_from_ext_id(file_ext_id, session=session)
        sanitized_res = _sanitize_res(result)
        file_ext.set_result(probe, sanitized_res)
        scan_id = file_ext.scan.external_id
        log.info("scan %s: file %s result from %s",
                 scan_id, file_ext_id, probe)
    is_finished(scan_id)


def set_status(scan_id, status):
    log.debug("scan %s: set status %s", scan_id, status)
    with session_transaction() as session:
        scan = Scan.load_from_ext_id(scan_id, session=session)
        scan.set_status(status)


# insure there is only one call running at a time
# among the different workers
@interprocess_locked(interprocess_lock_path)
def is_finished(scan_id):
    with session_transaction() as session:
        scan = Scan.load_from_ext_id(scan_id, session)
        log.debug("scan %s: is_finished %d/%d", scan_id,
                  scan.probes_finished, scan.probes_total)
        if scan.finished() and scan.status != IrmaScanStatus.finished:
            # call finished hook for each files
            for file_ext in scan.files_ext:
                file_ext.hook_finished()
            scan.set_status(IrmaScanStatus.finished)
            session.commit()
            # launch flush celery task on brain
            log.debug("scan %s: calling scan_flush", scan.external_id)
            celery_brain.scan_flush(scan.external_id)


def handle_output_files(file_ext_id, result, error_case=False):
    log.info("Handling output for file %s", file_ext_id)
    with session_transaction() as session:
        file_ext = FileExt.load_from_ext_id(file_ext_id, session)
        scan = file_ext.scan
        uploaded_files = result.get('uploaded_files', None)
        log.debug("scan %s file %s depth %s", scan.external_id,
                  file_ext_id, file_ext.depth)
        if uploaded_files is None:
            return
        resubmit = scan.resubmit_files
        max_resubmit_level = get_max_resubmit_level()
        if max_resubmit_level != 0 and file_ext.depth > \
                max_resubmit_level:
            log.warning("scan %s file %s resubmit level %s exceeded max "
                        "level (%s)", scan.external_id,
                        file_ext_id, file_ext.depth,
                        max_resubmit_level
                        )
            resubmit = False
        if not resubmit or error_case:
            reason = "Error case" if error_case else "Resubmit disabled"
            log.debug("scan %s: %s flushing files", scan.external_id, reason)
            celery_brain.files_flush(list(uploaded_files.values()),
                                     scan.external_id)
            return
        log.debug("scan %s: found files %s", scan.external_id, uploaded_files)
        # Retrieve the DB probe_result to link it with
        # a new FileProbeResult in _append_new_files
        probe_result = file_ext.fetch_probe_result(result['name'])
        new_fws = _append_new_files_to_scan(scan, uploaded_files,
                                            probe_result, file_ext.depth+1)
        parent_file = file_ext.file
        for new_fw in new_fws:
            parent_file.children.append(new_fw)
        session.commit()
        log.debug("scan %s: %d new files to resubmit",
                  scan.external_id, len(new_fws))

        scan_request = _create_scan_request(new_fws,
                                            scan.get_probelist(),
                                            scan.mimetype_filtering)
        scan_request = _add_empty_results(new_fws, scan_request, scan, session)
        if scan_request.nb_files == 0:
            scan.set_status(IrmaScanStatus.finished)
            log.info("scan %s: nothing to do flushing files",
                     scan.external_id)
            celery_brain.files_flush(list(uploaded_files.values()),
                                     scan.external_id)
            return
        for new_fw in new_fws:
            celery_brain.scan_launch(new_fw.external_id,
                                     new_fw.probes,
                                     scan.external_id)
    return


def generate_csv_report_as_stream(scan_proxy):
    # If you try to use the `scan_proxy` object, it won't be available anymore
    # as the session (from Hug middleware) has already been closed.
    with session_query() as session:
        # Using this `merge` function with `load=False` will prevent the ORM to
        # entirely query the object from the database.
        scan = session.merge(scan_proxy, load=False)

        # CSV Header
        header = [
            "Date",
            "MD5",
            "SHA1",
            "SHA256",
            "Filename",
            "First seen",
            "Last seen",
            "Size",
            "Status",
            "Submitter",
            "Submitter's IP address",
        ]

        if scan.files_ext:
            # To display the probe list (with the right names), we use an
            # file_ext value from the database, and iterate over the probes
            # needed. This is a workaround, as getting the list of Probes
            # directly from the scan object (using Scan `get_probelist()`
            # function) doesn't provide the information regarding the Probe
            # type (Antivirus, External, …).
            probe_results = scan.files_ext[0].get_probe_results()

            try:
                # Python3, Dict `.keys()` function doesn't return a list, but
                # an `dict_keys`.
                # Casting is needed here for further list concatenation.
                av_list = list(probe_results['antivirus'].keys())
            except KeyError:
                av_list = []

            try:
                external_list = [name for name in probe_results['external']
                                 if name == 'VirusTotal']
            except KeyError:
                external_list = []

            header += (av_list + external_list)

        # The `str` cast (via the map function) is only there in case a Probe
        # name isn't a string, which will break the `bytes` convert.
        yield bytes(CSV_SEPARATOR.join(map(str, header)), 'utf-8')
        yield b"\r\n"

        # CSV rows
        for f in scan.files_ext:
            row = [
                scan.date,
                f.file.md5,
                f.file.sha1,
                f.file.sha256,
                f.name,
                f.file.timestamp_first_scan,
                f.file.timestamp_last_scan,
                f.file.size,
                f.status,
                f.submitter,
                scan.ip,
            ]

            probe_results = f.get_probe_results()

            row.extend(probe_results['antivirus'][name]['status'] for name in
                       av_list)
            row.extend(probe_results['external'][name]['results'] for name in
                       external_list)

            yield bytes(CSV_SEPARATOR.join(map(str, row)), 'utf-8')
            yield b"\r\n"
