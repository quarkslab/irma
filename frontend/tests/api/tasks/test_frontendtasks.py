from unittest import TestCase

from mock import patch

import api.tasks.frontendtasks as module


class TestModuleFrontendtasks(TestCase):

    @patch("api.tasks.frontendtasks.async_call")
    def test_scan_launch(self, m_async_call):
        arg = "whatever"
        module.scan_launch(arg)
        m_async_call.assert_called()
