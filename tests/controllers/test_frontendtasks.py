from unittest import TestCase
from mock import patch
import frontend.controllers.frontendtasks as module


class TestModuleFrontendtasks(TestCase):

    def test001_scan_launch(self):
        with patch("frontend.controllers.frontendtasks.async_call") as mock:
            arg = "whatever"
            module.scan_launch(arg)
        self.assertTrue(mock.called)
