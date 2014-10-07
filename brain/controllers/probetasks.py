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

import celery
import time
import config.parser as config
from brain.helpers.celerytasks import route, async_call


results_app = celery.Celery('resultstasks')
config.conf_results_celery(results_app)

probe_app = celery.Celery('probetasks')
config.conf_results_celery(probe_app)

# Time to cache the probe list
# to avoid asking to rabbitmq
PROBELIST_CACHE_TIME = 60
cache_probelist = {'list': None, 'time': None}


def get_probelist():
    # get active queues list from probe celery app
    now = time.time()
    result_queue = config.brain_config['broker_probe'].queue
    if cache_probelist['time'] is not None:
        cache_time = now - cache_probelist['time']
    if cache_probelist['time'] is None or cache_time > PROBELIST_CACHE_TIME:
        slist = list()
        i = probe_app.control.inspect()
        queues = i.active_queues()
        if queues:
            for infolist in queues.values():
                for info in infolist:
                    if info['name'] not in slist:
                        # exclude only predefined result queue
                        if info['name'] != result_queue:
                            slist.append(info['name'])
        if len(slist) != 0:
            # activate cache only on non empty list
            cache_probelist['time'] = now
        cache_probelist['list'] = slist
    return cache_probelist['list']


# ============
#  Task calls
# ============

def job_launch(ftpuser, frontend_scanid, filename, probe, job_id):
    """ send a task to the brain to flush the scan files"""
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
                      link_error=hook_error)
    return task.id


def job_cancel(job_list):
    probe_app.control.revoke(job_list, terminate=True)
