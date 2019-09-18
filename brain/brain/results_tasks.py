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

import config.parser as config

import celery
import logging
from celery.utils.log import get_task_logger
import brain.controllers.probectrl as probe_ctrl
import brain.controllers.frontendtasks as celery_frontend
from brain.helpers.sql import session_query


# Get celery's logger
log = get_task_logger(__name__)

results_app = celery.Celery('resultstasks')
config.conf_results_celery(results_app)
config.configure_syslog(results_app)

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
#  Tasks declaration
# ===================

@results_app.task(ignore_result=True, acks_late=True)
def job_success(result, file, probe):
    try:
        log.info("file:%s probe %s",
                 file, probe)
        celery_frontend.scan_result(file, probe, result)
    except Exception as e:
        log.exception(type(e).__name__ + " : " + str(e))
        raise job_success.retry(countdown=5, max_retries=3, exc=e)


@results_app.task(ignore_result=True, acks_late=True)
def job_error(parent_taskid, file, probe):
    try:
        log.info("file:%s probe %s", file, probe)
        with session_query() as session:
            result = probe_ctrl.create_error_results(probe, "job error",
                                                     session)
            celery_frontend.scan_result(file, probe, result)
    except Exception as e:
        log.exception(type(e).__name__ + " : " + str(e))
        raise job_error.retry(countdown=5, max_retries=3, exc=e)


########################
# command line launcher
########################


if __name__ == '__main__':
    options = config.get_celery_options("brain.results_tasks",
                                        "brain_results_app")
    results_app.worker_main(options)
