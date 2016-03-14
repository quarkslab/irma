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

import re
import time
import celery
import logging
from celery import Celery
from celery.utils.log import get_task_logger
from celery.exceptions import TimeoutError
import brain.controllers.userctrl as user_ctrl
import brain.controllers.scanctrl as scan_ctrl
import brain.controllers.jobctrl as job_ctrl
import brain.controllers.probectrl as probe_ctrl
import brain.controllers.probetasks as celery_probe
import brain.controllers.frontendtasks as celery_frontend
import brain.controllers.ftpctrl as ftp_ctrl
from lib.irma.common.utils import IrmaTaskReturn, IrmaScanStatus, \
    IrmaScanRequest
from lib.common.utils import UUID
from fasteners import interprocess_locked


# Get celery's logger
log = get_task_logger(__name__)

scan_app = Celery('scantasks')
config.conf_brain_celery(scan_app)
config.configure_syslog(scan_app)

results_app = Celery('resultstasks')
config.conf_results_celery(results_app)
config.configure_syslog(results_app)

probe_app = Celery('probetasks')
config.conf_probe_celery(probe_app)
config.configure_syslog(probe_app)

interprocess_lock_path = config.get_lock_path()

# IRMA specific debug messages are enables through
# config file Section: log / Key: debug
if config.debug_enabled():
    def after_setup_logger_handler(sender=None, logger=None, loglevel=None,
                                   logfile=None, format=None,
                                   colorize=None, **kwds):
        config.setup_debug_logger(logging.getLogger(__name__))
        log.debug("debug is enabled")
    celery.signals.after_setup_logger.connect(after_setup_logger_handler)
    celery.signals.after_setup_task_logger.connect(after_setup_logger_handler)

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
    log.debug("scanid: %s received %s", frontend_scanid, scan_request_dict)
    scan_request = IrmaScanRequest(scan_request_dict)
    scan_id = scan_ctrl.new(frontend_scanid, user_id, scan_request.nb_files)
    (remaining, quota) = user_ctrl.get_quota(user_id)
    if remaining is not None:
        log.info("scanid %s: quota remaining {0}/{1}",
                 frontend_scanid,
                 remaining,
                 quota)
    else:
        log.info("scanid %s: unlimited quota",
                 frontend_scanid)
    if remaining <= 0:
        scan_ctrl.error(scan_id, IrmaScanStatus.error)
    return scan_id


def _get_mimetype_probelist(mimetype):
    log.debug("asking what probes handle %s", mimetype)
    probe_list = []
    for p in probe_ctrl.get_all():
        probe_name = p.name
        regexp = p.mimetype_regexp
        if regexp is None or \
           re.search(regexp, mimetype, re.IGNORECASE) is not None:
            probe_list.append(probe_name)
    log.debug("probes: %s", "-".join(probe_list))
    return probe_list

# Time to cache the probe list
# to avoid asking to rabbitmq
PROBELIST_CACHE_TIME = 30
cache_probelist = {'list': None, 'time': None}


# as the method for querying active_queues is not forksafe
# insure there is only one call running at a time
# among the different workers
@interprocess_locked(interprocess_lock_path)
def active_probes():
    global cache_probelist
    # get active queues list from probe celery app
    now = time.time()
    if cache_probelist['time'] is not None:
        cache_time = now - cache_probelist['time']
    if cache_probelist['time'] is None or cache_time > PROBELIST_CACHE_TIME:
        log.debug("refreshing cached list")
        # scan all active queues except result queue
        # to list all probes queues ready
        plist = []
        queues = probe_app.control.inspect().active_queues()
        if queues:
            result_queue = config.brain_config['broker_probe'].queue
            for queuelist in queues.values():
                for queue in queuelist:
                    # exclude only predefined result queue
                    if queue['name'] != result_queue:
                        plist.append(queue['name'])
        if len(plist) != 0:
            # activate cache only on non empty list
            cache_probelist['time'] = now
        cache_probelist['list'] = sorted(plist)
    log.debug("probe_list: %s", "-".join(cache_probelist['list']))
    return cache_probelist['list']


def refresh_probes():
    probe_ctrl.all_offline()
    for probe in active_probes():
        celery_probe.get_info(probe)
    return

# Refresh all probes before starting
refresh_probes()


# ===================
#  Tasks declaration
# ===================

@scan_app.task(acks_late=True)
def register_probe(name, category, mimetype_filter):
    try:
        log.info("probe %s category %s registered [%s] transfer to scan_app",
                 name, category, mimetype_filter)
        probe_ctrl.register(name, category, mimetype_filter)
        return
    except Exception as e:
        log.exception(e)
        raise register_probe.retry(countdown=5, max_retries=3, exc=e)


@scan_app.task(acks_late=True)
def probe_list():
    probe_list = probe_ctrl.get_all_probename()
    active_probes_list = active_probes()
    offline_probe = filter(lambda x: x not in active_probes_list, probe_list)
    if len(offline_probe) != 0:
        for probe in offline_probe:
            probe_ctrl.set_offline(probe)
        log.info("probe list set_offline [%s]", ",".join(offline_probe))
    online_probe = filter(lambda x: x not in probe_list, active_probes_list)
    if len(online_probe) != 0:
        for probe in online_probe:
            probe_ctrl.set_online(probe)
        log.info("probe list set_online [%s]", ",".join(online_probe))
    probe_list = probe_ctrl.get_all_probename()
    return IrmaTaskReturn.success(probe_list)


@scan_app.task(ignore_result=False, acks_late=True)
def mimetype_filter_scan_request(scan_request_dict):
    try:
        available_probelist = probe_ctrl.get_all_probename()
        scan_request = IrmaScanRequest(scan_request_dict)
        for filehash in scan_request.filehashes():
            filtered_probelist = []
            mimetype = scan_request.get_mimetype(filehash)
            mimetype_probelist = _get_mimetype_probelist(mimetype)
            probe_list = scan_request.get_probelist(filehash)
            log.debug("filehash: %s probe_list: %s",
                      filehash, "-".join(probe_list))
            # first check probe_list for unknown probe
            for probe in probe_list:
                # check if probe exists
                if probe not in available_probelist:
                    msg = "Unknown probe {0}".format(probe)
                    log.error(msg)
                    return IrmaTaskReturn.error(msg)
                if probe in mimetype_probelist:
                    # probe is asked but not supported by mimetype
                    log.debug("filehash %s probe %s asked but" +
                              " not supported for %s",
                              filehash, probe, mimetype)
                    filtered_probelist.append(probe)
            # update probe list in scan request
            scan_request.set_probelist(filehash, filtered_probelist)
        return IrmaTaskReturn.success(scan_request.to_dict())
    except Exception as e:
        log.exception(e)
        raise


@scan_app.task(ignore_result=False, acks_late=True)
def scan(frontend_scanid, scan_request_dict):
    try:
        log.debug("scanid %s: new_scan", frontend_scanid)
        scan_id = _create_scan(frontend_scanid, scan_request_dict)
        scan_request = IrmaScanRequest(scan_request_dict)
        available_probelist = probe_ctrl.get_all_probename()
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
                    msg = "unknown probe {0}".format(probe)
                    log.error("scanid %s: unknown probe %s",
                              frontend_scanid,
                              probe)
                    return IrmaTaskReturn.error(msg)
            if probe_list is None:
                scan_ctrl.error(scan_id, IrmaScanStatus.error_probe_missing)
                log.error("scanid %s empty probe list", frontend_scanid)
                return IrmaTaskReturn.error("empty probe list on brain")
            # Now, create one subtask per file to
            # scan per probe according to quota
            for probe in probe_list:
                if remaining is not None:
                    if remaining <= 0:
                        log.error("scanid %s: scan quota exceeded",
                                  frontend_scanid)
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
        log.info("scanid %s: %d file(s) received / %d active probe(s) / "
                 "%d job(s) launched",
                 frontend_scanid,
                 scan_request.nb_files,
                 len(available_probelist),
                 scan_ctrl.get_nbjobs(scan_id))
    except Exception as e:
        log.exception(e)
        raise


@scan_app.task(acks_late=True)
def scan_cancel(frontend_scanid):
    try:
        log.info("scanid %s: cancelling", frontend_scanid)
        rmqvhost = config.get_frontend_rmqvhost()
        user_id = user_ctrl.get_userid(rmqvhost)
        scan_id = scan_ctrl.get_scan_id(frontend_scanid, user_id)
        (status, progress_details) = scan_ctrl.progress(scan_id)
        log.debug("scanid %s: progress_details %s",
                  frontend_scanid, progress_details)
        scan_ctrl.cancelling(scan_id)
        pending_jobs = scan_ctrl.get_pending_jobs(scan_id)
        cancel_details = None
        log.info("scanid %s: %d pending jobs",
                 frontend_scanid, len(pending_jobs))
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
        log.exception(e)
        return IrmaTaskReturn.error("cancel error on brain")


@results_app.task(ignore_result=True, acks_late=True)
def job_success(result, jobid):
    try:
        (frontend_scanid, filename, probe) = job_ctrl.info(jobid)
        log.info("scanid %s: jobid:%d probe %s",
                 frontend_scanid, jobid, probe)
        celery_frontend.scan_result(frontend_scanid, filename, probe, result)
        job_ctrl.success(jobid)
        return
    except Exception as e:
        log.exception(e)
        raise job_success.retry(countdown=5, max_retries=3, exc=e)


@results_app.task(ignore_result=True, acks_late=True)
def job_error(parent_taskid, jobid):
    try:
        (frontend_scanid, filename, probe) = job_ctrl.info(jobid)
        log.info("scanid %s: jobid:%d probe %s",
                 frontend_scanid, jobid, probe)
        job_ctrl.error(jobid)
        result = {}
        result['status'] = -1
        result['name'] = probe
        result['type'] = probe_ctrl.get_category(probe)
        result['error'] = "Brain job error"
        result['duration'] = job_ctrl.duration(jobid)
        celery_frontend.scan_result(frontend_scanid, filename, probe, result)
    except Exception as e:
        log.exception(e)
        raise job_error.retry(countdown=5, max_retries=3, exc=e)


@results_app.task(ignore_result=True, acks_late=True)
def scan_flush(frontend_scanid):
    try:
        log.info("scan_id %s: scan flush requested", frontend_scanid)
        rmqvhost = config.get_frontend_rmqvhost()
        user_id = user_ctrl.get_userid(rmqvhost)
        scan_id = scan_ctrl.get_scan_id(frontend_scanid, user_id)
        log.info("flush brain_scan_id %s", scan_id)
        scan_ctrl.flush(scan_id)
        ftpuser = user_ctrl.get_ftpuser(user_id)
        ftp_ctrl.flush_dir(ftpuser, frontend_scanid)
    except Exception as e:
        log.exception(e)
        return
