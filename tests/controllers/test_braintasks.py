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

    @patch("frontend.controllers.braintasks.sync_call")
    def test001_probe_list_raise_task(self, m_sync_call):
        expected = "test"
        m_sync_call.return_value = (IrmaReturnCode.error, expected)
        with self.assertRaises(IrmaTaskError) as context:
            module.probe_list()
        self.assertEqual(str(context.exception), expected)
        m_sync_call.assert_called_once()

    @patch("frontend.controllers.braintasks.sync_call")
    def test002_probe_list_raise_core(self, m_sync_call):
        expected = "no probe available"
        m_sync_call.return_value = (IrmaReturnCode.success, list())
        with self.assertRaises(IrmaCoreError) as context:
            module.probe_list()
        self.assertEqual(str(context.exception), expected)
        m_sync_call.assert_called_once()

    @patch("frontend.controllers.braintasks.sync_call")
    def test003_probe_list_ok(self, m_sync_call):
        expected = ["test"]
        m_sync_call.return_value = (IrmaReturnCode.success, expected)
        self.assertEqual(module.probe_list(), expected)

    @patch("frontend.controllers.braintasks.sync_call")
    def test004_scan_progress(self, m_sync_call):
        arg = "test"
        result = module.scan_progress(arg)
        m_sync_call.assert_called_once_with(self.m_brain_app,
                                            "brain.tasks",
                                            "scan_progress",
                                            self.m_timeout,
                                            args=[arg])
        self.assertEqual(result, m_sync_call())

    @patch("frontend.controllers.braintasks.sync_call")
    def test005_scan_cancel(self, m_sync_call):
        arg = "test"
        result = module.scan_cancel(arg)
        m_sync_call.assert_called_once_with(self.m_brain_app,
                                            "brain.tasks",
                                            "scan_cancel",
                                            self.m_timeout,
                                            args=[arg])
        self.assertEqual(result, m_sync_call())

    @patch("frontend.controllers.braintasks.async_call")
    def test006_scan_launch(self, m_async_call):
        args = ["test1", "test2"]
        result = module.scan_launch(*args)
        m_async_call.assert_called_once_with(self.m_brain_app,
                                             "brain.tasks",
                                             "scan",
                                             args=args)
        self.assertEqual(result, m_async_call())

    @patch("frontend.controllers.braintasks.async_call")
    def test007_scan_flush(self, m_async_call):
        arg = "test"
        result = module.scan_flush(arg)
        m_async_call.assert_called_once_with(self.m_brain_app,
                                             "brain.tasks",
                                             "scan_flush",
                                             args=[arg])
        self.assertEqual(result, m_async_call())

    @patch("frontend.controllers.braintasks.sync_call")
    def test008_mimetype_filter_raise_task(self, m_sync_call):
        expected = "test"
        m_sync_call.return_value = (IrmaReturnCode.error, expected)
        with self.assertRaises(IrmaTaskError) as context:
            module.mimetype_filter_scan_request("whatever")
        self.assertEqual(str(context.exception), expected)

    @patch("frontend.controllers.braintasks.sync_call")
    def test009_mimetype_filter_ok(self, m_sync_call):
        expected = "test"
        m_sync_call.return_value = (IrmaReturnCode.success, expected)
        res = module.mimetype_filter_scan_request("whatever")
        self.assertEqual(res, expected)
