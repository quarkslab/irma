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


import celery
import logging
import config.parser as config
from celery.utils.log import get_task_logger
from fasteners import interprocess_locked
from brain.models.sqlobjects import User, Job, Scan
import brain.controllers.scanctrl as scan_ctrl
import brain.controllers.probectrl as probe_ctrl
import brain.controllers.probetasks as celery_probe
import brain.controllers.frontendtasks as celery_frontend
from brain.helpers.sql import session_transaction
from lib.irma.common.utils import IrmaTaskReturn, IrmaScanStatus, \
    IrmaScanRequest


# Get celery's logger
log = get_task_logger(__name__)

scan_app = celery.Celery('scantasks')
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

# Refresh all probes before starting
with session_transaction() as session:
    probe_ctrl.refresh_probes(session)


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
        log.exception(e)
        raise register_probe.retry(countdown=5, max_retries=3, exc=e)


@scan_app.task(acks_late=True)
def probe_list():
    try:
        with session_transaction() as session:
            probe_list = probe_ctrl.get_list(session)
            return IrmaTaskReturn.success(probe_list)
    except Exception as e:
        log.exception(e)
        return IrmaTaskReturn.error("Error getting probelist")


@scan_app.task(ignore_result=False, acks_late=True)
def mimetype_filter_scan_request(scan_request_dict):
    try:
        with session_transaction() as session:
            available_probelist = probe_ctrl.get_list(session)
            scan_request = IrmaScanRequest(scan_request_dict)
            for filehash in scan_request.filehashes():
                filtered_probelist = []
                mimetype = scan_request.get_mimetype(filehash)
                mimetype_probelist = probe_ctrl.mimetype_probelist(mimetype,
                                                                   session)
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
        with session_transaction() as session:
            log.debug("scanid: %s received %s", frontend_scanid,
                      scan_request_dict)
            user = User.get_by_rmqvhost(session)
            scan_request = IrmaScanRequest(scan_request_dict)
            scan = scan_ctrl.new(frontend_scanid, user, scan_request.nb_files,
                                 session)
            available_probelist = probe_ctrl.get_list(session)
            # Now, create one subtask per file to
            # scan per probe
            new_jobs = []
            for filehash in scan_request.filehashes():
                probelist = scan_request.get_probelist(filehash)
                scan_ctrl.check_probelist(scan, probelist,
                                          available_probelist, session)
                for probe in probelist:
                    j = Job(scan.id, filehash, probe)
                    session.add(j)
                    new_jobs.append(j)
            session.commit()
            scan_ctrl.launch(scan, new_jobs, session)
            celery_frontend.scan_launched(scan.scan_id,
                                          scan_request.to_dict())
            log.info("scanid %s: %d file(s) received / %d active probe(s) / "
                     "%d job(s) launched",
                     scan.scan_id,
                     scan.nb_files,
                     len(available_probelist),
                     len(scan.jobs))
    except Exception as e:
        log.exception(e)
        raise


@scan_app.task(acks_late=True)
def scan_cancel(frontend_scan_id):
    try:
        with session_transaction() as session:
            user = User.get_by_rmqvhost(session)
            scan = Scan.get_scan(frontend_scan_id, user.id, session)
            res = scan_ctrl.cancel(scan, session)
            return IrmaTaskReturn.success(res)
    except Exception as e:
        log.exception(e)
        return IrmaTaskReturn.error("cancel error on brain")


@scan_app.task(ignore_result=True, acks_late=True)
def scan_flush(frontend_scan_id):
    try:
        log.info("scan_id %s: scan flush requested", frontend_scan_id)
        with session_transaction() as session:
            user = User.get_by_rmqvhost(session)
            scan = Scan.get_scan(frontend_scan_id, user.id, session)
            scan_ctrl.flush(scan, session)
    except Exception as e:
        log.exception(e)
        return
