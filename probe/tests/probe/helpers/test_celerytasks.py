from unittest import TestCase

from mock import MagicMock
import probe.helpers.celerytasks as module


class TestCelerytasks(TestCase):

    def test_async_call_raise(self):
        app = MagicMock()
        app.send_task.side_effect = TimeoutError("whatever")
        path, name = "p_test", "n_test"
        expected = "Celery error - %s" % name
        with self.assertRaises(module.IrmaTaskError) as context:
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
