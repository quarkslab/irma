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

import celery
import config.parser as config
from frontend.helpers.celerytasks import sync_call, async_call
from lib.irma.common.exceptions import IrmaCoreError, IrmaTaskError
from lib.irma.common.utils import IrmaReturnCode

timeout = config.get_brain_celery_timeout()
brain_app = celery.Celery('braintasks')
config.conf_brain_celery(brain_app)

# ============
#  Task calls
# ============


def probe_list():
    """ send a task to the brain asking for active probe list """
    (retcode, res) = sync_call(brain_app,
                               "brain.tasks",
                               "probe_list",
                               timeout)
    if retcode != IrmaReturnCode.success:
        raise IrmaTaskError(res)
    if len(res) == 0:
        raise IrmaCoreError("no probe available")
    return res


def scan_progress(scanid):
    """ send a task to the brain asking for status of subtasks launched """
    return sync_call(brain_app,
                     "brain.tasks",
                     "scan_progress",
                     timeout,
                     args=[scanid])


def scan_cancel(scanid):
    """ send a task to the brain to cancel all remaining subtasks """
    return sync_call(brain_app,
                     "brain.tasks",
                     "scan_cancel",
                     timeout,
                     args=[scanid])


def scan_launch(scanid, scan_request):
    """ send a task to the brain to start the scan """
    return async_call(brain_app,
                      "brain.tasks",
                      "scan",
                      args=[scanid, scan_request])


def scan_flush(scanid):
    """ send a task to the brain to flush the scan files"""
    return async_call(brain_app,
                      "brain.tasks",
                      "scan_flush",
                      args=[scanid])
