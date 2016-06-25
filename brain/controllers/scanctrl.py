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
import brain.controllers.probetasks as celery_probe
import brain.controllers.ftpctrl as ftp_ctrl
from lib.irma.common.utils import IrmaScanStatus
from lib.irma.common.exceptions import IrmaDatabaseResultNotFound

log = logging.getLogger(__name__)


def new(frontend_scan_id, user, nb_files, session):
    try:
        scan = Scan.get_scan(frontend_scan_id, user.id, session)
        scan.nb_files += nb_files
        scan.update(['nb_files'], session)
    except IrmaDatabaseResultNotFound:
        scan = Scan(frontend_scan_id, user.id, nb_files)
        scan.save(session)
    session.commit()
    log.debug("scanid %s: user_id %s nb_files %s id %s",
              frontend_scan_id, user.id, nb_files, scan.id)
    return scan


def set_status(scan, status, session):
    if status not in IrmaScanStatus.label.keys():
        raise ValueError("Unknown status %s", status)
    scan.status = status
    session.commit()


def check_probelist(scan, probelist, available_probelist, session):
    if probelist is None:
        set_status(scan, IrmaScanStatus.error_probe_missing, session)
        msg = "empty probe list"
        log.error("scanid %s: %s", scan.scan_id, msg)
        raise ValueError(msg)
    for probe in probelist:
        # check if probe exists
        if probe not in available_probelist:
            set_status(scan, IrmaScanStatus.error_probe_missing, session)
            msg = "unknown probe {0}".format(probe)
            log.error("scanid %s: %s", scan.scan_id, msg)
            raise ValueError(msg)


def flush(scan, session):
    if scan.status == IrmaScanStatus.flushed:
        log.info("scan_id %s: already flushed", scan.scan_id)
        return
    log.debug("scan_id %s: flush scan %s", scan.scan_id, scan.id)
    ftpuser = scan.user.ftpuser
    ftp_ctrl.flush_dir(ftpuser, scan.scan_id)
    jobs = scan.jobs
    log.debug("scan_id %s: delete %s jobs", scan.scan_id, len(jobs))
    for job in jobs:
        session.delete(job)
    set_status(scan, IrmaScanStatus.flushed, session)
    return


def launch(scan, jobs, session):
    ftpuser = scan.user.ftpuser
    frontend_scanid = scan.scan_id
    for job in jobs:
        filehash = job.filehash
        probename = job.probename
        task_id = job.task_id
        celery_probe.job_launch(ftpuser, frontend_scanid, filehash,
                                probename, task_id)
    set_status(scan, IrmaScanStatus.launched, session)
    return


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
