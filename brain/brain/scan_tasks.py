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


import celery
import logging
import time
import config.parser as config
from celery.utils.log import get_task_logger
from fasteners import interprocess_locked
from brain.models.sqlobjects import User, Job, Scan
import brain.controllers.ftpctrl as ftp_ctrl
import brain.controllers.scanctrl as scan_ctrl
import brain.controllers.probectrl as probe_ctrl
import brain.controllers.frontendtasks as celery_frontend
from brain.helpers.sql import session_transaction
from irma.common.base.utils import IrmaTaskReturn, IrmaScanRequest

RETRY_MAX_DELAY = 30

# Get celery's logger
log = get_task_logger(__name__)

scan_app = celery.Celery('scan_tasks')
config.conf_brain_celery(scan_app)
config.configure_syslog(scan_app)

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

delay = 1
while True:
    try:
        # Refresh all probes before starting
        with session_transaction() as session:
            probe_ctrl.refresh_probelist(session)
        break
    except OSError as e:
        log.error("Error refreshing probe %s waiting %s seconds", e, delay)
        time.sleep(delay)
        delay = min([2*delay, RETRY_MAX_DELAY])
        pass


# ===================
#  Tasks declaration
# ===================

@scan_app.task(acks_late=True)
@interprocess_locked(interprocess_lock_path)
def register_probe(name, display_name, category, mimetype_filter):
    try:
        log.info("probe %s category %s registered [%s] transfer to scan_app",
                 name, category, mimetype_filter)
        with session_transaction() as session:
            probe_ctrl.register(name, display_name, category,
                                mimetype_filter, session)
    except Exception as e:
        log.exception(type(e).__name__ + " : " + str(e))
        raise register_probe.retry(countdown=5, max_retries=3, exc=e)


@scan_app.task(acks_late=True)
def probe_list():
    # convert to list because ListProxy is not serializable
    probes = list(probe_ctrl.available_probes)
    return IrmaTaskReturn.success(probes)


@scan_app.task
def probe_list_refresh():
    try:
        with session_transaction() as session:
            probe_ctrl.refresh_probelist(session)
    except Exception as e:
        log.exception(type(e).__name__ + " : " + str(e))
        return IrmaTaskReturn.error("Error getting probelist")


@scan_app.task(ignore_result=False, acks_late=True)
def mimetype_filter_scan_request(scan_request_dict):
    try:
        with session_transaction() as session:
            scan_request = IrmaScanRequest(scan_request_dict)
            for file in scan_request.files():
                filtered_probelist = []
                mimetype = scan_request.get_mimetype(file)
                mimetype_probelist = probe_ctrl.mimetype_probelist(mimetype,
                                                                   session)
                probe_list = scan_request.get_probelist(file)
                log.debug("file: %s probe_list: %s",
                          file, "-".join(probe_list))
                # first check probe_list for unknown probe
                for probe in probe_list:
                    # check if probe exists
                    if probe not in probe_ctrl.available_probes:
                        log.warning("probe %s not available", probe)
                    if probe in mimetype_probelist:
                        # probe is asked and supported by mimetype
                        log.debug("file %s probe %s asked" +
                                  " and supported for %s append to request",
                                  file, probe, mimetype)
                        filtered_probelist.append(probe)
                # update probe list in scan request
                scan_request.set_probelist(file, filtered_probelist)
            return IrmaTaskReturn.success(scan_request.to_dict())
    except Exception as e:
        log.exception(type(e).__name__ + " : " + str(e))
        return IrmaTaskReturn.error("Brain error")


@scan_app.task(ignore_result=False, acks_late=True)
def scan(file, probelist, frontend_scan):
    try:
        with session_transaction() as session:
            log.debug("scan_id: %s fileweb_id: %s received %s", frontend_scan,
                      file, probelist)
            user = User.get_by_rmqvhost(session)
            scan = scan_ctrl.new(frontend_scan, user, session)
            # Now, create one subtask per file to scan per probe
            new_jobs = []
            for probe in probelist:
                if probe in probe_ctrl.available_probes:
                    j = Job(scan.id, file, probe)
                    session.add(j)
                    new_jobs.append(j)
                else:
                    # send an error message to not stuck the scan
                    # One probe asked is no more present
                    res = probe_ctrl.create_error_results(probe,
                                                          "missing probe",
                                                          session)
                    celery_frontend.scan_result(file,
                                                probe,
                                                res)
            session.commit()
            scan_ctrl.launch(scan, new_jobs, session)
            log.info("scan_id %s: file %s received / %d active probe(s) / "
                     "%d job(s) launched",
                     scan.scan_id,
                     file,
                     len(probe_ctrl.available_probes),
                     len(scan.jobs))
    except Exception as e:
        log.exception(type(e).__name__ + " : " + str(e))
        raise


@scan_app.task(acks_late=True)
def scan_cancel(scan_id):
    try:
        log.info("scan %s: cancel", scan_id)
        with session_transaction() as session:
            user = User.get_by_rmqvhost(session)
            scan = Scan.get_scan(scan_id, user.id, session)
            res = scan_ctrl.cancel(scan, session)
            return IrmaTaskReturn.success(res)
    except Exception as e:
        log.exception(type(e).__name__ + " : " + str(e))
        return IrmaTaskReturn.error("cancel error on brain")


@scan_app.task(ignore_result=True, acks_late=True)
def scan_flush(scan_id):
    try:
        log.info("scan %s: flush requested", scan_id)
        with session_transaction() as session:
            user = User.get_by_rmqvhost(session)
            scan = Scan.get_scan(scan_id, user.id, session)
            scan_ctrl.flush(scan, session)
    except Exception as e:
        log.exception(type(e).__name__ + " : " + str(e))
        return


@scan_app.task(ignore_result=True, acks_late=True)
def files_flush(files, scan_id):
    try:
        with session_transaction() as session:
            user = User.get_by_rmqvhost(session)
            scan = Scan.get_scan(scan_id, user.id, session)
            ftpuser = scan.user.ftpuser
            log.debug("Flushing files %s", files)
            ftp_ctrl.flush(ftpuser, files)
    except Exception as e:
        log.exception(type(e).__name__ + " : " + str(e))
        return

########################
# command line launcher
########################


if __name__ == '__main__':
    options = config.get_celery_options("brain.scan_tasks",
                                        "scan_app")
    scan_app.worker_main(options)
