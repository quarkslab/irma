from unittest import TestCase
from mock import patch, MagicMock
from bottle import Bottle

import frontend.api.v1_1.errors as api_errors
from lib.irma.common.exceptions import IrmaDatabaseResultNotFound, \
    IrmaDatabaseError


class TestApiErrors(TestCase):

    def test001_initiation(self):
        t_type = "type"
        t_message = "message"
        error = api_errors.ApiError(t_type, t_message)
        self.assertEqual(error.__repr__(),
                         '<ApiError(type={self.type!r}, '
                         'message={self.message!r})'.format(self=error))

    @patch("frontend.api.v1_1.errors.abort")
    @patch("frontend.api.v1_1.errors.sys")
    def test002_process_value_error(self, m_sys, m_abort):
        m_sys.exc_info.return_value = (MagicMock(), None, MagicMock())
        error = ValueError("message_error")
        exp_code = 402
        exp_error = api_errors.ApiError("value_error", str(error))
        api_errors.process_error(error)
        m_abort.assert_called_once()
        call_args = m_abort.call_args[0]
        self.assertEqual(call_args[0], exp_code)
        self.assertEqual(str(call_args[1]), str(exp_error))

    @patch("frontend.api.v1_1.errors.abort")
    @patch("frontend.api.v1_1.errors.sys")
    def test003_process_notfound_error(self, m_sys, m_abort):
        m_sys.exc_info.return_value = (MagicMock(), None, MagicMock())
        error = IrmaDatabaseResultNotFound("message_error")
        exp_code = 404
        exp_error = api_errors.ApiError("request_error", "Object not Found")
        api_errors.process_error(error)
        m_abort.assert_called_once()
        call_args = m_abort.call_args[0]
        self.assertEqual(call_args[0], exp_code)
        self.assertEqual(str(call_args[1]), str(exp_error))

    @patch("frontend.api.v1_1.errors.abort")
    @patch("frontend.api.v1_1.errors.sys")
    def test004_process_database_error(self, m_sys, m_abort):
        m_sys.exc_info.return_value = (MagicMock(), None, MagicMock())
        error = IrmaDatabaseError("message_error")
        exp_code = 402
        exp_error = api_errors.ApiError("database_error")
        api_errors.process_error(error)
        m_abort.assert_called_once()
        call_args = m_abort.call_args[0]
        self.assertEqual(call_args[0], exp_code)
        self.assertEqual(str(call_args[1]), str(exp_error))

    @patch("frontend.api.v1_1.errors.api_error_schema")
    def test005_define_errors(self, m_error_schema):
        application = Bottle()
        api_errors.define_errors(application)
        self.assertTrue(404 in application.error_handler.keys())
        self.assertTrue(402 in application.error_handler.keys())
        handler = application.error_handler[404]
        error = MagicMock()
        handler(error)
        m_error_schema.dumps.assert_called_with(error.body)
