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
import brain.controllers.frontendtasks as module


class TestFrontendTasks(TestCase):

    @patch("brain.controllers.frontendtasks.async_call")
    def test_scan_result(self, m_async_call):
        filename = "filename"
        probe = "probe"
        result = "result"
        module.scan_result(filename, probe, result)
        hook_error = module.route(
                        module.frontend_app.signature(
                                "frontend_app.scan_result_error",
                                [filename, probe, result]))
        m_async_call.assert_called_once_with(module.frontend_app,
                                             "frontend_app",
                                             "scan_result",
                                             args=[filename,
                                                   probe, result],
                                             link_error=hook_error)
