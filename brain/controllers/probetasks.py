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
from brain.helpers.celerytasks import route, async_call

results_app = celery.Celery('resultstasks')
config.conf_results_celery(results_app)

probe_app = celery.Celery('probetasks')
config.conf_probe_celery(probe_app)

log = logging.getLogger(__name__)


# ============
#  Task calls
# ============

def job_launch(ftpuser, frontend_scanid, filename, probe, job_id, task_id):
    """ send a task to the brain to flush the scan files"""
    log.debug("scanid %s: ftpuser %s filename %s probe %s" +
              " job_id %s task_id %s",
              frontend_scanid, ftpuser, filename, probe, job_id, task_id)
    hook_success = route(
        results_app.signature("brain.tasks.job_success",
                              [job_id]))
    hook_error = route(
        results_app.signature("brain.tasks.job_error",
                              [job_id]))
    task = async_call(probe_app,
                      "probe.tasks",
                      "probe_scan",
                      args=(ftpuser, frontend_scanid, filename),
                      queue=probe,
                      link=hook_success,
                      link_error=hook_error,
                      uuid=task_id)
    return task.id


def job_cancel(job_list):
    log.debug("job_list: %s", "-".join(job_list))
    probe_app.control.revoke(job_list, terminate=True)


def get_info(queue_name):
    log.debug("queue_name: %s", queue_name)
    async_call(probe_app,
               "probe.tasks",
               "register",
               queue=queue_name)
    return
