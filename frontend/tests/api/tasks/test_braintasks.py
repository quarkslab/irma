from unittest import TestCase

from mock import MagicMock, patch

import api.tasks.braintasks as module
from api.tasks.braintasks import BRAIN_SCAN_TASKS
from irma.common.base.exceptions import IrmaCoreError, IrmaTaskError
from irma.common.base.utils import IrmaReturnCode


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

    @patch("api.tasks.braintasks.sync_call")
    def test001_probe_list_raise_task(self, m_sync_call):
        expected = "test"
        m_sync_call.return_value = (IrmaReturnCode.error, expected)
        with self.assertRaises(IrmaTaskError) as context:
            module.probe_list()
        self.assertEqual(str(context.exception), expected)
        m_sync_call.assert_called_once()

    @patch("api.tasks.braintasks.sync_call")
    def test002_probe_list_raise_core(self, m_sync_call):
        expected = "no probe available"
        m_sync_call.return_value = (IrmaReturnCode.success, list())
        with self.assertRaises(IrmaCoreError) as context:
            module.probe_list()
        self.assertEqual(str(context.exception), expected)
        m_sync_call.assert_called_once()

    @patch("api.tasks.braintasks.sync_call")
    def test003_probe_list_ok(self, m_sync_call):
        expected = ["test"]
        m_sync_call.return_value = (IrmaReturnCode.success, expected)
        self.assertEqual(module.probe_list(), expected)

    @patch("api.tasks.braintasks.sync_call")
    def test004_scan_progress(self, m_sync_call):
        arg = "test"
        result = module.scan_progress(arg)
        m_sync_call.assert_called_once_with(self.m_brain_app,
                                            BRAIN_SCAN_TASKS,
                                            "scan_progress",
                                            self.m_timeout,
                                            args=[arg])
        self.assertEqual(result, m_sync_call())

    @patch("api.tasks.braintasks.sync_call")
    def test005_scan_cancel(self, m_sync_call):
        arg = "test"
        result = module.scan_cancel(arg)
        m_sync_call.assert_called_once_with(self.m_brain_app,
                                            BRAIN_SCAN_TASKS,
                                            "scan_cancel",
                                            self.m_timeout,
                                            args=[arg])
        self.assertEqual(result, m_sync_call())

    @patch("api.tasks.braintasks.async_call")
    def test006_scan_launch(self, m_async_call):
        args = ["test1", "test2", "test3"]
        result = module.scan_launch(*args)
        m_async_call.assert_called_once_with(self.m_brain_app,
                                             BRAIN_SCAN_TASKS,
                                             "scan",
                                             args=args)
        self.assertEqual(result, m_async_call())

    @patch("api.tasks.braintasks.async_call")
    def test007_scan_flush(self, m_async_call):
        arg = "test"
        result = module.scan_flush(arg)
        m_async_call.assert_called_once_with(self.m_brain_app,
                                             BRAIN_SCAN_TASKS,
                                             "scan_flush",
                                             args=[arg])
        self.assertEqual(result, m_async_call())

    @patch("api.tasks.braintasks.sync_call")
    def test008_mimetype_filter_raise_task(self, m_sync_call):
        expected = "test"
        m_sync_call.return_value = (IrmaReturnCode.error, expected)
        with self.assertRaises(IrmaTaskError) as context:
            module.mimetype_filter_scan_request("whatever")
        self.assertEqual(str(context.exception), expected)

    @patch("api.tasks.braintasks.sync_call")
    def test009_mimetype_filter_ok(self, m_sync_call):
        expected = "test"
        m_sync_call.return_value = (IrmaReturnCode.success, expected)
        res = module.mimetype_filter_scan_request("whatever")
        self.assertEqual(res, expected)
