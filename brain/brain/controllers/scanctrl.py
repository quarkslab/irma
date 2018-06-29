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
from brain.models.sqlobjects import Scan
import brain.controllers.probetasks as celery_probe
import brain.controllers.ftpctrl as ftp_ctrl
from irma.common.base.utils import IrmaScanStatus
from irma.common.base.exceptions import IrmaDatabaseResultNotFound
import config.parser as config
from fasteners import interprocess_locked

interprocess_lock_path = config.get_lock_path()
log = logging.getLogger(__name__)


@interprocess_locked(interprocess_lock_path)
def new(frontend_scan_id, user, session):
    try:
        scan = Scan.get_scan(frontend_scan_id, user.id, session)
    except IrmaDatabaseResultNotFound:
        scan = Scan(frontend_scan_id, user.id)
        session.add(scan)
        session.commit()
    log.debug("scanid %s: user_id %s id %s",
              frontend_scan_id, user.id, scan.id)
    return scan


def set_status(scan, status, session):
    if status not in IrmaScanStatus.label.keys():
        raise ValueError("Unknown status %s", status)
    scan.status = status
    session.commit()


@interprocess_locked(interprocess_lock_path)
def flush(scan, session):
    if scan.status == IrmaScanStatus.flushed:
        log.info("scan_id %s: already flushed", scan.scan_id)
        return
    log.debug("scan_id %s: flush scan %s", scan.scan_id, scan.id)
    ftpuser = scan.user.ftpuser
    log.debug("Flushing files %s", scan.files)
    ftp_ctrl.flush(ftpuser, scan.files)
    log.debug("scan_id %s: delete %s jobs", scan.scan_id, len(scan.jobs))
    for job in scan.jobs:
        session.delete(job)
    set_status(scan, IrmaScanStatus.flushed, session)
    return


def launch(scan, jobs, session):
    ftpuser = scan.user.ftpuser
    for job in jobs:
        filename = job.filename
        probename = job.probename
        task_id = job.task_id
        celery_probe.job_launch(ftpuser, filename,
                                probename, task_id)
    set_status(scan, IrmaScanStatus.launched, session)
    return


@interprocess_locked(interprocess_lock_path)
def cancel(scan, session):
    log.info("scanid %s: cancelling", scan.scan_id)
    status = IrmaScanStatus.label[scan.status]
    set_status(scan, IrmaScanStatus.cancelling, session)
    pending_jobs = [j.task_id for j in scan.jobs]
    log.info("scanid %s: %d jobs",
             scan.scan_id, len(pending_jobs))
    if len(pending_jobs) != 0:
        celery_probe.job_cancel(pending_jobs)
    set_status(scan, IrmaScanStatus.cancelled, session)
    flush(scan, session)
    res = dict()
    res['status'] = status
    res['cancel_details'] = None
    return res
