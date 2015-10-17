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

import config.parser as config

from celery import Celery
from celery.utils.log import get_task_logger
import brain.controllers.userctrl as user_ctrl
import brain.controllers.scanctrl as scan_ctrl
import brain.controllers.jobctrl as job_ctrl
import brain.controllers.probetasks as celery_probe
import brain.controllers.frontendtasks as celery_frontend
import brain.controllers.ftpctrl as ftp_ctrl
from lib.irma.common.utils import IrmaTaskReturn, IrmaScanStatus, \
    IrmaScanRequest
from lib.common.utils import UUID

# Get celery's logger
log = get_task_logger(__name__)

scan_app = Celery('scantasks')
config.conf_brain_celery(scan_app)
config.configure_syslog(scan_app)

results_app = Celery('resultstasks')
config.conf_results_celery(results_app)
config.configure_syslog(results_app)


# ===================
#  Private functions
# ===================


def _create_scan(frontend_scanid, scan_request_dict):
    # TODO user should be identified by RMQ vhost
    # read vhost from config as workaround
    rmqvhost = config.get_frontend_rmqvhost()
    user_id = user_ctrl.get_userid(rmqvhost)
    # create an initial entry to track future errors
    # tell frontend that frontend_scanid is now known to brain
    # progress available
    print("Received {0}".format(scan_request_dict))
    scan_request = IrmaScanRequest(scan_request_dict)
    scan_id = scan_ctrl.new(frontend_scanid, user_id, scan_request.nb_files)
    (remaining, quota) = user_ctrl.get_quota(user_id)
    if remaining is not None:
        log.info("%s quota remaining {0}/{1}",
                 frontend_scanid,
                 remaining,
                 quota)
    else:
        log.info("%s unlimited quota",
                 frontend_scanid)
    if remaining <= 0:
        scan_ctrl.error(scan_id, IrmaScanStatus.error)
    return scan_id


mimetype_probe = {}


def _get_mimetype_probelist(mimetype):
    log.info("asking what probes handle %s",
             mimetype)
    available_probelist = celery_probe.get_probelist()
    if mimetype not in mimetype_probe:
        mimetype_probe[mimetype] = []
        for probe in available_probelist:
            res = celery_probe.handle_mimetype(mimetype, probe).get()
            if res is True:
                mimetype_probe[mimetype].append(probe)
                log.info("probe %s handle it", probe)
    return mimetype_probe[mimetype]


# ===================
#  Tasks declaration
# ===================


@scan_app.task(acks_late=True)
def probe_list():
    try:
        probe_list = celery_probe.get_probelist()
        if len(probe_list) > 0:
            return IrmaTaskReturn.success(probe_list)
        else:
            return IrmaTaskReturn.error("no probe available")
    except:
        log.info("exception", exc_info=True)
        raise


@scan_app.task(ignore_result=False, acks_late=True)
def mimetype_filter_scan_request(scan_request_dict):
    try:
        available_probelist = celery_probe.get_probelist()
        scan_request = IrmaScanRequest(scan_request_dict)
        for filehash in scan_request.filehashes():
            filtered_probelist = []
            mimetype = scan_request.get_mimetype(filehash)
            mimetype_probelist = _get_mimetype_probelist(mimetype)
            probe_list = scan_request.get_probelist(filehash)
            # first check probe_list for unknown probe
            for probe in probe_list:
                # check if probe exists
                if probe not in available_probelist:
                    msg = "Unknown probe {0}".format(probe)
                    log.info("Unknown probe %s",
                             probe)
                    return IrmaTaskReturn.error(msg)
                if probe in mimetype_probelist:
                    # probe is asked but not supported by mimetype
                    filtered_probelist.append(probe)
            # update probe list in scan request
            scan_request.set_probelist(filehash, filtered_probelist)
        return IrmaTaskReturn.success(scan_request.to_dict())
    except:
        log.info("exception", exc_info=True)
        raise


@scan_app.task(ignore_result=False, acks_late=True)
def scan(frontend_scanid, scan_request_dict):
    try:
        log.info("%s: new_scan", frontend_scanid)
        scan_id = _create_scan(frontend_scanid, scan_request_dict)
        scan_request = IrmaScanRequest(scan_request_dict)
        available_probelist = celery_probe.get_probelist()
        log.info("%s: launch_scan", frontend_scanid)
        user_id = scan_ctrl.get_user_id(scan_id)
        (remaining, _) = user_ctrl.get_quota(user_id)
        ftp_user = user_ctrl.get_ftpuser(user_id)
        for filehash in scan_request.filehashes():
            probe_list = scan_request.get_probelist(filehash)
            # first check probe_list for unknown probe
            for probe in probe_list:
                # check if probe exists
                if probe not in available_probelist:
                    scan_ctrl.error(scan_id,
                                    IrmaScanStatus.error_probe_missing)
                    msg = "Unknown probe {0}".format(probe)
                    log.info("%s Unknown probe %s",
                             frontend_scanid,
                             probe)
                    return IrmaTaskReturn.error(msg)
            if probe_list is None:
                scan_ctrl.error(scan_id, IrmaScanStatus.error_probe_missing)
                log.info("%s Empty probe list", frontend_scanid)
                return IrmaTaskReturn.error("empty probe list on brain")
            # Now, create one subtask per file to
            # scan per probe according to quota
            for probe in probe_list:
                if remaining is not None:
                    if remaining <= 0:
                        break
                    else:
                        remaining -= 1
                task_id = UUID.generate()
                job_id = job_ctrl.new(scan_id, filehash, probe, task_id)
                celery_probe.job_launch(ftp_user,
                                        frontend_scanid,
                                        filehash,
                                        probe,
                                        job_id,
                                        task_id)
        scan_ctrl.launched(scan_id)
        celery_frontend.scan_launched(frontend_scanid, scan_request.to_dict())
        log.info(
            "%s %d files receives / %d active probes / "
            "%d jobs launched",
            frontend_scanid,
            scan_request.nb_files,
            len(available_probelist),
            scan_ctrl.get_nbjobs(scan_id))
    except:
        log.info("exception", exc_info=True)
        raise


@scan_app.task(acks_late=True)
def scan_cancel(frontend_scanid):
    try:
        log.info("scanid %s", frontend_scanid)
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
    except:
        log.info("exception", exc_info=True)
        return IrmaTaskReturn.error("cancel error on brain")


@results_app.task(ignore_result=True, acks_late=True)
def job_success(result, jobid):
    try:
        (frontend_scanid, filename, probe) = job_ctrl.info(jobid)
        log.info("scanid %s jobid:%d probe %s",
                 frontend_scanid,
                 jobid,
                 probe)
        celery_frontend.scan_result(frontend_scanid, filename, probe, result)
        job_ctrl.success(jobid)
    except:
        log.info("exception", exc_info=True)
        return


@results_app.task(ignore_result=True, acks_late=True)
def job_error(parent_taskid, jobid):
    try:
        (frontend_scanid, filename, probe) = job_ctrl.info(jobid)
        log.info("scanid %s jobid:%d probe %s",
                 frontend_scanid, jobid, probe)
        job_ctrl.error(jobid)
        result = {}
        result['status'] = -1
        result['name'] = probe
        result['error'] = "Brain job error"
        result['duration'] = job_ctrl.duration(jobid)
        celery_frontend.scan_result(frontend_scanid, filename, probe, result)
    except:
        log.info("exception", exc_info=True)
        return


@results_app.task(ignore_result=True, acks_late=True)
def scan_flush(frontend_scanid):
    try:
        log.info("scan_id %s scan flush requested", frontend_scanid)
        rmqvhost = config.get_frontend_rmqvhost()
        user_id = user_ctrl.get_userid(rmqvhost)
        scan_id = scan_ctrl.get_scan_id(frontend_scanid, user_id)
        scan_ctrl.flush(scan_id)
        ftpuser = user_ctrl.get_ftpuser(user_id)
        ftp_ctrl.flush_dir(ftpuser, frontend_scanid)
    except:
        log.info("exception", exc_info=True)
        return
