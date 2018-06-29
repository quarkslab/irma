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

import config.parser as config
from api.common.celery import sync_call, async_call
from irma.common.base.exceptions import IrmaCoreError, IrmaTaskError
from irma.common.base.utils import IrmaReturnCode

timeout = config.get_brain_celery_timeout()
brain_app = celery.Celery('braintasks')
config.conf_brain_celery(brain_app)

BRAIN_SCAN_TASKS = "brain.scan_tasks"

# ============
#  Task calls
# ============


def probe_list():
    """ send a task to the brain asking for active probe list """
    (retcode, res) = sync_call(brain_app,
                               BRAIN_SCAN_TASKS,
                               "probe_list",
                               timeout)
    if retcode != IrmaReturnCode.success:
        raise IrmaTaskError(res)
    if len(res) == 0:
        raise IrmaCoreError("no probe available")
    return res


def mimetype_filter_scan_request(scan_request):
    """ send a task to the brain asking for mimetype filtering
        on probe list
    """
    (retcode, res) = sync_call(brain_app,
                               BRAIN_SCAN_TASKS,
                               "mimetype_filter_scan_request",
                               timeout,
                               args=[scan_request])
    if retcode != IrmaReturnCode.success:
        raise IrmaTaskError(res)
    return res


def scan_progress(scan_id):
    """ send a task to the brain asking for status of subtasks launched """
    return sync_call(brain_app,
                     BRAIN_SCAN_TASKS,
                     "scan_progress",
                     timeout,
                     args=[scan_id])


def scan_cancel(scan_id):
    """ send a task to the brain to cancel all remaining subtasks """
    return sync_call(brain_app,
                     BRAIN_SCAN_TASKS,
                     "scan_cancel",
                     timeout,
                     args=[scan_id])


def scan_launch(fileid, probelist, scan_id):
    """ send a task to the brain to start the scan """
    return async_call(brain_app,
                      BRAIN_SCAN_TASKS,
                      "scan",
                      args=[fileid, probelist, scan_id])


def scan_flush(scan_id):
    """ send a task to the brain to flush the scan files"""
    return async_call(brain_app,
                      BRAIN_SCAN_TASKS,
                      "scan_flush",
                      args=[scan_id])


def files_flush(files, scan_id):
    """ send a task to the brain to flush additional scan files"""
    return async_call(brain_app,
                      BRAIN_SCAN_TASKS,
                      "files_flush",
                      args=[files, scan_id])
