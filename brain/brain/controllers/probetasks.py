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
import config.parser as config
from brain.helpers.celerytasks import route, async_call

results_app = celery.Celery('resultstasks')
config.conf_results_celery(results_app)

probe_app = celery.Celery('probetasks')
config.conf_probe_celery(probe_app)

log = logging.getLogger(__name__)


# ============
#  Task calls
# ============

def job_launch(ftpuser, filename, probename, task_id):
    """ send a task to the brain to flush the scan files"""
    log.debug("ftpuser %s filename %s probe %s" +
              " task_id %s",
              ftpuser, filename, probename, task_id)
    hook_success = route(
        results_app.signature("brain.results_tasks.job_success",
                              [filename, probename]))
    hook_error = route(
        results_app.signature("brain.results_tasks.job_error",
                              [filename, probename]))
    exchange = probename + "_exchange"
    task = async_call(probe_app,
                      "probe.tasks",
                      "probe_scan",
                      args=(ftpuser, filename),
                      routing_key=probename,
                      exchange=exchange,
                      link=hook_success,
                      link_error=hook_error,
                      task_id=task_id)
    return task.id


def job_cancel(job_list):
    log.debug("job_list: %s", " / ".join(job_list))
    probe_app.control.revoke(job_list, terminate=True)


def get_info(queue_name):
    log.debug("queue_name: %s", queue_name)
    async_call(probe_app,
               "probe.tasks",
               "register",
               routing_key=queue_name)
    return
