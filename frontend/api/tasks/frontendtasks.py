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
from api.common.celery import async_call

frontend_app = celery.Celery('frontend_app')
config.conf_frontend_celery(frontend_app)

# ============
#  Task calls
# ============


def scan_launch(scanid):
    """ send a task to launch the scan """
    async_call(frontend_app,
               "frontend_app",
               "scan_launch",
               args=(scanid,))
