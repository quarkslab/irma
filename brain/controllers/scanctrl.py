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
from brain.models.sqlobjects import Scan
from brain.helpers.sql import session_query, session_transaction
from lib.irma.common.utils import IrmaScanStatus
from lib.irma.common.exceptions import IrmaValueError, \
    IrmaDatabaseResultNotFound

log = logging.getLogger(__name__)


def new(frontend_scan_id, user_id, nb_files):
    with session_transaction() as session:
        try:
            scan = Scan.get_scan(frontend_scan_id, user_id, session)
            scan.nb_files += nb_files
            scan.update(['nb_files'], session)
        except IrmaDatabaseResultNotFound:
            scan = Scan(frontend_scan_id, user_id, nb_files)
            scan.save(session)
        session.commit()
        log.debug("scanid %s: user_id %s nb_files %s id %s",
                  frontend_scan_id, user_id, nb_files, scan.id)
        return scan.id


def get_scan_id(frontend_scan_id, user_id):
    with session_query() as session:
        scan = Scan.get_scan(frontend_scan_id, user_id, session)
        log.debug("scanid %s: user_id %s id %s",
                  frontend_scan_id, user_id, scan.id)
        return scan.id


def get_user_id(scan_id):
    with session_query() as session:
        scan = Scan.load(scan_id, session)
        log.debug("user_id: %s", scan.user_id)
        return scan.user_id


def get_nbjobs(scan_id):
    with session_query() as session:
        scan = Scan.load(scan_id, session)
        log.debug("nb_jobs: %s", scan.nb_jobs)
        return scan.nb_jobs


def _set_status(scan_id, code):
    log.debug("brain_scan_id: %s code %s", scan_id, code)
    with session_transaction() as session:
        scan = Scan.load(scan_id, session)
        scan.status = code
        session.commit()


def cancelling(scan_id):
    _set_status(scan_id, IrmaScanStatus.cancelling)


def cancelled(scan_id):
    _set_status(scan_id, IrmaScanStatus.cancelled)


def launched(scan_id):
    _set_status(scan_id, IrmaScanStatus.launched)


def progress(scan_id):
    log.debug("brain_scan_id: %s", scan_id)
    with session_query() as session:
        scan = Scan.load(scan_id, session)
        if IrmaScanStatus.is_error(scan.status):
            status_str = IrmaScanStatus.label[scan.status]
            log.error("status %s", status_str)
            raise IrmaValueError(status_str)
        status = IrmaScanStatus.label[scan.status]
        progress_details = None
        if scan.status == IrmaScanStatus.launched:
            (total, finished, success) = scan.progress()
            progress_details = {}
            progress_details['total'] = total
            progress_details['finished'] = finished
            progress_details['successful'] = success
        log.debug("%s", progress_details)
        return (status, progress_details)


def get_pending_jobs(scan_id):
    with session_query() as session:
        scan = Scan.load(scan_id, session)
        return scan.get_pending_jobs_taskid()


def check_finished(scan_id):
    with session_transaction() as session:
        scan = Scan.load(scan_id, session)
        if scan.status == IrmaScanStatus.processed:
            return True
        if scan.finished():
            scan.status = IrmaScanStatus.processed
            return True
        return False


def flush(scan_id):
    with session_transaction() as session:
        scan = Scan.load(scan_id, session)
        if scan.status == IrmaScanStatus.flushed:
            return
        for job in scan.jobs:
            log.debug("delete job %s", job.id)
            session.delete(job)
        scan.status = IrmaScanStatus.flushed


def error(scan_id, code):
    with session_transaction() as session:
        scan = Scan.load(scan_id, session)
        scan.status = code
