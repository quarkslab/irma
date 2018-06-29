from unittest import TestCase

from celery.exceptions import TimeoutError
from mock import MagicMock

import api.common.celery as module
from irma.common.base.exceptions import IrmaTaskError


class TestModuleCelerytasks(TestCase):

    def test_sync_call_raise(self):
        app = MagicMock()
        app.send_task.side_effect = TimeoutError("whatever")
        path, name, timeout = "p_test", "n_test", "t_test"
        expected = "Celery timeout - %s" % name
        with self.assertRaises(IrmaTaskError) as context:
            module.sync_call(app, path, name, timeout)
        self.assertEqual(str(context.exception), expected)

    def test_sync_call_ok(self):
        app = MagicMock()
        path, name, timeout, karg = "p_test", "n_test", "t_test", "k_test"
        expected = ("s_test", "r_test")
        args = (("%s.%s" % (path, name),), {"karg": karg})
        app.send_task().get.return_value = expected
        result = module.sync_call(app, path, name, timeout, karg=karg)
        self.assertEqual(result, expected)
        self.assertEqual(app.send_task.call_args, args)
        self.assertEqual(app.send_task().get.call_args,
                         (tuple(), {"timeout": timeout}))

    def test_async_call_raise(self):
        app = MagicMock()
        app.send_task.side_effect = TimeoutError("whatever")
        path, name = "p_test", "n_test"
        expected = "Celery error - %s" % name
        with self.assertRaises(IrmaTaskError) as context:
            module.async_call(app, path, name)
        self.assertEqual(str(context.exception), expected)

    def test_async_call_ok(self):
        app = MagicMock()
        path, name, karg = "p_test", "n_test", "k_test"
        expected = ("s_test", "r_test")
        args = (("%s.%s" % (path, name),), {"karg": karg})
        app.send_task.return_value = expected
        result = module.async_call(app, path, name, karg=karg)
        self.assertEqual(result, expected)
        self.assertEqual(app.send_task.call_args, args)
