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

import config.parser as config

from celery import Celery
from celery.utils.log import get_task_logger
import brain.controllers.userctrl as user_ctrl
import brain.controllers.scanctrl as scan_ctrl
import brain.controllers.jobctrl as job_ctrl
import brain.controllers.probetasks as celery_probe
import brain.controllers.frontendtasks as celery_frontend
import brain.controllers.ftpctrl as ftp_ctrl
from lib.irma.common.utils import IrmaTaskReturn, IrmaScanStatus
from lib.irma.common.exceptions import IrmaTaskError

# Get celery's logger
log = get_task_logger(__name__)

scan_app = Celery('scantasks')
config.conf_brain_celery(scan_app)
config.configure_syslog(scan_app)

results_app = Celery('resultstasks')
config.conf_results_celery(results_app)
config.configure_syslog(results_app)


# ===================
#  Tasks declaration
# ===================

@scan_app.task(acks_late=True)
def probe_list():
    probe_list = celery_probe.get_probelist()
    if len(probe_list) > 0:
        return IrmaTaskReturn.success(probe_list)
    else:
        return IrmaTaskReturn.error("No probe available")


@scan_app.task(ignore_result=True, acks_late=True)
def scan(frontend_scanid, scan_request):
    log.info("{0}: scan launched".format(frontend_scanid))
    # TODO user should be identified by RMQ vhost
    # read vhost from config as workaround
    rmqvhost = config.get_frontend_rmqvhost()
    user_id = user_ctrl.get_userid(rmqvhost)
    ftpuser = user_ctrl.get_ftpuser(user_id)
    # create an initial entry to track future errors
    # tell frontend that frontend_scanid is now known to brain
    # progress available
    scan_id = scan_ctrl.new(frontend_scanid, user_id, len(scan_request))
    # send a scan launched event to frontend
    (remaining, quota) = user_ctrl.get_quota(user_id)
    log.info("{0}: Found user".format(frontend_scanid) +
             "quota remaining {0}/{1}".format(remaining, quota))
    if remaining <= 0:
        scan_ctrl.error(scan_id, IrmaScanStatus.error)

    available_probelist = celery_probe.get_probelist()
    for (filename, probe_list) in scan_request.items():
        if probe_list is None:
            scan_ctrl.error(scan_id, IrmaScanStatus.error_probe_missing)
            log.info("{0}: Empty probe list".format(frontend_scanid))
            return IrmaTaskReturn.error("BrainTask: Empty probe list")
        # first check probe_list
        for p in probe_list:
            # check if probe exists
            if p not in available_probelist:
                scan_ctrl.error(scan_id, IrmaScanStatus.error_probe_missing)
                msg = "BrainTask: Unknown probe {0}".format(p)
                log.info("{0}: Unknown probe {1}".format(frontend_scanid, p))
                return IrmaTaskReturn.error(msg)

        # an array with link between job and celery task
        # to insert them all at once in db
        job_task_tuples = []
        for probe in probe_list:
            # Now, create one subtask per file to
            # scan per probe according to quota
            if remaining is not None:
                if remaining <= 0:
                    break
                else:
                    remaining -= 1
            job_id = job_ctrl.new(scan_id, filename, probe)
            task_id = celery_probe.job_launch(ftpuser,
                                              frontend_scanid,
                                              filename,
                                              probe,
                                              job_id)
            job_task_tuples.append((job_id, task_id))
    job_ctrl.set_taskids(job_task_tuples)
    scan_ctrl.launched(scan_id)
    celery_frontend.scan_launched(frontend_scanid)
    log.info(
        "{0}: ".format(frontend_scanid) +
        "{0} files receives / ".format(len(scan_request)) +
        "{0} active probe / ".format(len(available_probelist)) +
        "{0} probe used / ".format(len(probe_list)) +
        "{0} jobs launched".format(scan_ctrl.get_nbjobs(scan_id)))


@scan_app.task(acks_late=True)
def scan_progress(frontend_scanid):
    try:
        log.info("{0}: scan progress".format(frontend_scanid))
        rmqvhost = config.get_frontend_rmqvhost()
        user_id = user_ctrl.get_userid(rmqvhost)
        scan_id = scan_ctrl.get_scan_id(frontend_scanid, user_id)
        (status, progress_details) = scan_ctrl.progress(scan_id)
        res = {}
        res['status'] = status
        res['progress_details'] = progress_details
        return IrmaTaskReturn.success(res)
    except Exception as e:
        msg = "Brain: progress error {0}".format(e)
        return IrmaTaskReturn.error(msg)


@scan_app.task(acks_late=True)
def scan_cancel(frontend_scanid):
    try:
        log.info("{0}: scan cancel".format(frontend_scanid))
        rmqvhost = config.get_frontend_rmqvhost()
        user_id = user_ctrl.get_userid(rmqvhost)
        scan_id = scan_ctrl.get_scan_id(frontend_scanid, user_id)
        (status, progress_details) = scan_ctrl.progress(scan_id)
        scan_ctrl.cancelling(scan_id)
        pending_jobs = scan_ctrl.get_pending_jobs(scan_id)
        cancel_details = None
        if len(pending_jobs) != 0:
            celery_probe.job_cancel(pending_jobs)
            cancel_details = {}
            cancel_details['total'] = progress_details['total']
            cancel_details['finished'] = progress_details['finished']
            cancel_details['cancelled'] = len(pending_jobs)
        scan_ctrl.cancelled(scan_id)
        scan_flush(frontend_scanid)
        res = {}
        res['status'] = status
        res['cancel_details'] = cancel_details
        return IrmaTaskReturn.success(res)
    except Exception as e:
        msg = "Brain: cancel error {0}".format(e)
        return IrmaTaskReturn.error(msg)


@results_app.task(ignore_result=True, acks_late=True)
def job_success(result, jobid):
    try:
        log.info("{0}: job success".format(jobid))
        (frontend_scanid, filename, probe) = job_ctrl.info(jobid)
        log.info("{0}: probe {1}".format(frontend_scanid, probe))
        celery_frontend.scan_result(frontend_scanid, filename, probe, result)
        job_ctrl.success(jobid)
    except IrmaTaskError as e:
        msg = "Brain: result error {0}".format(e)
        return IrmaTaskReturn.error(msg)


@results_app.task(ignore_result=True, acks_late=True)
def job_error(parent_taskid, jobid):
    try:
        log.info("{0}: job error on {1}".format(jobid, parent_taskid))
        (frontend_scanid, filename, probe) = job_ctrl.info(jobid)
        log.info("{0}: probe {1}".format(frontend_scanid, probe))
        job_ctrl.error(jobid)
        result = {}
        result['status'] = -1
        result['name'] = probe
        result['error'] = "Brain job error"
        result['duration'] = job_ctrl.duration(jobid)
        celery_frontend.scan_result(frontend_scanid, filename, probe, result)
    except IrmaTaskError as e:
        msg = "Brain: result error {0}".format(e)
        return IrmaTaskReturn.error(msg)


@results_app.task(ignore_result=True, acks_late=True)
def scan_flush(frontend_scanid):
    try:
        log.info("{0} scan flush requested".format(frontend_scanid))
        rmqvhost = config.get_frontend_rmqvhost()
        user_id = user_ctrl.get_userid(rmqvhost)
        scan_id = scan_ctrl.get_scan_id(frontend_scanid, user_id)
        scan_ctrl.flush(scan_id)
        ftpuser = user_ctrl.get_ftpuser(user_id)
        ftp_ctrl.flush_dir(ftpuser, frontend_scanid)
    except Exception as e:
        log.info("{0} flush error {1}".format(scan_id, e))
        return
