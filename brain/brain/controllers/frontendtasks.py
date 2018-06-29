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
from brain.helpers.celerytasks import async_call, route

frontend_app = celery.Celery('frontend_app')
config.conf_frontend_celery(frontend_app)
config.configure_syslog(frontend_app)


def scan_result(file, probe, result):
    hook_error = route(frontend_app.signature("frontend_app.scan_result_error",
                       [file, probe, result]))
    async_call(frontend_app,
               "frontend_app",
               "scan_result",
               args=[file, probe, result],
               link_error=hook_error
               )
