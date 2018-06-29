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

from unittest import TestCase
from mock import patch
import brain.controllers.probetasks as module
from brain.helpers.celerytasks import route


class TestProbeTasks(TestCase):

    @patch("brain.controllers.probetasks.async_call")
    def test_job_launch(self, m_async_call):
        ftpuser = "ftpuser"
        filename = "filename"
        probe = "probe"
        task_id = "task_id"
        signature = module.results_app.signature
        hook_success = route(signature("brain.results_tasks.job_success",
                                       [filename, probe]))
        hook_error = route(signature("brain.results_tasks.job_error",
                                     [filename, probe]))
        exchange = probe + "_exchange"
        module.job_launch(ftpuser, filename, probe, task_id)
        m_async_call.assert_called_once_with(module.probe_app,
                                             "probe.tasks",
                                             "probe_scan",
                                             args=(ftpuser, filename),
                                             routing_key=probe,
                                             exchange=exchange,
                                             link=hook_success,
                                             link_error=hook_error,
                                             task_id=task_id)

    @patch("brain.controllers.probetasks.probe_app")
    def test_job_cancel(self, m_probe_app):
        job_list = [str(x) for x in range(10)]
        module.job_cancel(job_list)
        m_probe_app.control.revoke.assert_called_once_with(job_list,
                                                           terminate=True)

    @patch("brain.controllers.probetasks.async_call")
    def test_get_info(self, m_async_call):
        queue_name = "queue_name"
        module.get_info(queue_name)
        m_async_call.assert_called_once_with(module.probe_app,
                                             "probe.tasks",
                                             "register",
                                             routing_key=queue_name)
