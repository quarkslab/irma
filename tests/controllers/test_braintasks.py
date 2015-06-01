from unittest import TestCase
from mock import MagicMock, patch

import frontend.controllers.braintasks as module
from lib.irma.common.utils import IrmaReturnCode
from lib.irma.common.exceptions import IrmaCoreError, IrmaTaskError


class TestModuleBraintasks(TestCase):

    def setUp(self):
        self.old_timeout, self.old_brain_app = module.timeout, module.brain_app
        self.m_timeout, self.m_brain_app = MagicMock(), MagicMock()
        module.timeout = self.m_timeout
        module.brain_app = self.m_brain_app


    def tearDown(self):
        module.timeout = self.old_timeout
        module.brain_app = self.old_brain_app
        del self.m_brain_app
        del self.m_timeout


    def test001_probe_list_raise_task(self):
        expected = "test"
        with patch("frontend.controllers.braintasks.sync_call") as mock:
            mock.return_value = (IrmaReturnCode.error, expected)
            with self.assertRaises(IrmaTaskError) as context:
                module.probe_list()
        self.assertEqual(str(context.exception), expected)


    def test002_probe_list_raise_core(self):
        expected = "no probe available"
        with patch("frontend.controllers.braintasks.sync_call") as mock:
            mock.return_value = (IrmaReturnCode.success, list())
            with self.assertRaises(IrmaCoreError) as context:
                module.probe_list()
        self.assertEqual(str(context.exception), expected)


    def test003_probe_list_ok(self):
        expected = ["test"]
        with patch("frontend.controllers.braintasks.sync_call") as mock:
            mock.return_value = (IrmaReturnCode.success, expected)
            self.assertEqual(module.probe_list(), expected)


    def test004_scan_progress(self):
        arg = "test"
        expected = ((self.m_brain_app, "brain.tasks", "scan_progress", self.m_timeout),
                    {"args": [arg]})
        with patch("frontend.controllers.braintasks.sync_call") as mock:
            result = module.scan_progress(arg)
        self.assertTrue(mock.called)
        self.assertEqual(mock.call_args, expected)
        self.assertEqual(result, mock())


    def test005_scan_cancel(self):
        arg = "test"
        expected = ((self.m_brain_app, "brain.tasks", "scan_cancel", self.m_timeout),
                    {"args": [arg]})
        with patch("frontend.controllers.braintasks.sync_call") as mock:
            result = module.scan_cancel(arg)
        self.assertTrue(mock.called)
        self.assertEqual(mock.call_args, expected)
        self.assertEqual(result, mock())


    def test006_scan_launch(self):
        args = ["test1", "test2"]
        expected = ((self.m_brain_app, "brain.tasks", "scan"), {"args": args})
        with patch("frontend.controllers.braintasks.async_call") as mock:
            result = module.scan_launch(*args)
        self.assertTrue(mock.called)
        self.assertEqual(mock.call_args, expected)
        self.assertEqual(result, mock())


    def test007_scan_flush(self):
        arg = "test"
        expected = ((self.m_brain_app, "brain.tasks", "scan_flush"), {"args": [arg]})
        with patch("frontend.controllers.braintasks.async_call") as mock:
            result = module.scan_flush(arg)
        self.assertTrue(mock.called)
        self.assertEqual(mock.call_args, expected)
        self.assertEqual(result, mock())
