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
import config.parser as config
from brain.helpers.celerytasks import async_call

frontend_app = celery.Celery('frontendtasks')
config.conf_frontend_celery(frontend_app)
config.configure_syslog(frontend_app)


def scan_launched(frontend_scanid, scan_request):
    async_call(frontend_app,
               "frontend.tasks",
               "scan_launched",
               args=[frontend_scanid, scan_request])


def scan_result(frontend_scanid, filename, probe, result):
    async_call(frontend_app,
               "frontend.tasks",
               "scan_result",
               args=[frontend_scanid, filename, probe, result])
