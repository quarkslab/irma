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
from brain.controllers import scanctrl
from brain.models.sqlobjects import Job
from brain.helpers.sql import session_query, session_transaction
from lib.common.compat import timestamp

log = logging.getLogger(__name__)


def new(scan_id, filename, probe, task_id):
    with session_transaction() as session:
        j = Job(filename, probe, scan_id, task_id)
        j.save(session)
        session.commit()
        log.debug("scanid %s: job %s for file %s probe %s task_id %s",
                  scan_id, j.id, filename, probe, task_id)
        return j.id


def _finish(job_id, status):
    log.debug("job_id: %s status %s", job_id, status)
    with session_transaction() as session:
        job = Job.load(job_id, session)
        job.status = status
        job.ts_end = timestamp()
        job.update(['status', 'ts_end'], session)
        scan_id = job.scan.id
    scanctrl.check_finished(scan_id)


def success(job_id):
    _finish(job_id, Job.success)


def error(job_id):
    _finish(job_id, Job.error)


def set_taskid(job_id, task_id):
    log.debug("job_id: %s task_id %s", job_id, task_id)
    with session_transaction() as session:
        job = Job.load(job_id, session)
        job.task_id = task_id


def info(job_id):
    with session_query() as session:
        job = Job.load(job_id, session)
        frontend_scan_id = job.scan.scan_id
        filename = job.filename
        probe = job.probename
        return (frontend_scan_id, filename, probe)


def duration(job_id):
    with session_query() as session:
        job = Job.load(job_id, session)
        return (job.ts_end - job.ts_start)
