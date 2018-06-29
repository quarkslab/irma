from unittest import TestCase

import api.common.errors as api_errors
from irma.common.base.exceptions import IrmaDatabaseResultNotFound, \
    IrmaDatabaseError


class TestCommonErrors(TestCase):

    def test_process_notfound_error(self):
        error = IrmaDatabaseResultNotFound("message_error")
        with self.assertRaises(api_errors.HTTPError) as context:
            try:
                raise error
            except Exception as e:
                api_errors.IrmaExceptionHandler.process_error(e)
        self.assertEqual(context.exception.title, "NoResultFound")

    def test_process_database_error(self):
        error = IrmaDatabaseError("message_error")
        with self.assertRaises(api_errors.HTTPInternalServerError) as context:
            try:
                raise error
            except Exception as e:
                api_errors.IrmaExceptionHandler.process_error(e)
        self.assertEqual(context.exception.title, "database_error")
