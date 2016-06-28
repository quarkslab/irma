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

from unittest import TestCase
from mock import patch
import brain.controllers.frontendtasks as module


class TestFrontendTasks(TestCase):

    @patch("brain.controllers.frontendtasks.async_call")
    def test001_scan_launched(self, m_async_call):
        frontend_scanid = "frontend_scanid"
        scan_request = "scan_request"
        module.scan_launched(frontend_scanid, scan_request)
        m_async_call.assert_called_once_with(module.frontend_app,
                                             "frontend.tasks",
                                             "scan_launched",
                                             args=[frontend_scanid,
                                                   scan_request])

    @patch("brain.controllers.frontendtasks.async_call")
    def test002_scan_result(self, m_async_call):
        frontend_scanid = "frontend_scanid"
        filename = "filename"
        probe = "probe"
        result = "result"
        module.scan_result(frontend_scanid, filename, probe, result)
        m_async_call.assert_called_once_with(module.frontend_app,
                                             "frontend.tasks",
                                             "scan_result",
                                             args=[frontend_scanid, filename,
                                                   probe, result])
