from unittest import TestCase

import api.common.errors as api_errors
from irma.common.base.exceptions import IrmaDatabaseResultNotFound, \
    IrmaDatabaseError


class TestCommonErrors(TestCase):

    def test_process_value_error(self):
        error = ValueError("message_error")
        with self.assertRaises(api_errors.HTTPInvalidParam) as context:
            try:
                raise error
            except Exception as e:
                api_errors.IrmaExceptionHandler("whatever", "whatever", e)
        self.assertEqual(context.exception.title, "Invalid parameter")

    def test_process_notfound_error(self):
        error = IrmaDatabaseResultNotFound("message_error")
        with self.assertRaises(api_errors.HTTPError) as context:
            try:
                raise error
            except Exception as e:
                api_errors.IrmaExceptionHandler("whatever", "whatever", e)
        self.assertEqual(context.exception.title, "NoResultFound")

    def test_process_database_error(self):
        error = IrmaDatabaseError("message_error")
        with self.assertRaises(api_errors.HTTPInternalServerError) as context:
            try:
                raise error
            except Exception as e:
                api_errors.IrmaExceptionHandler("whatever", "whatever", e)
        self.assertEqual(context.exception.title, "database_error")

    def test_process_unknown_error(self):
        error = Exception("message_error")
        with self.assertRaises(Exception) as context:
            try:
                raise error
            except Exception as e:
                api_errors.IrmaExceptionHandler("whatever", "whatever", e)
        self.assertEqual(context.exception, error)
