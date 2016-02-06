from unittest import TestCase
from mock import MagicMock, patch

import frontend.api.v1_1.controllers.files as api_files
from bottle import FormsDict


class TestApiSearch(TestCase):

    def setUp(self):
        self.old_file_web_schema = api_files.file_web_schema
        self.old_request = api_files.request
        self.file_web_schema = MagicMock()
        self.request = MagicMock()
        self.request.query = FormsDict()
        self.db = MagicMock()
        api_files.file_web_schema = self.file_web_schema
        api_files.request = self.request

    def tearDown(self):
        api_files.file_web_schema = self.old_file_web_schema
        api_files.request = self.old_request
        del self.file_web_schema
        del self.request

    def test001_files_raise_none_None(self):
        self.request.query['name'] = "whatever"
        self.request.query.hash = "something"
        process_error = "frontend.api.v1_1.controllers.files.process_error"
        with patch(process_error) as mock:
            api_files.list("whatever")
            self.assertTrue(mock.called)
            self.assertIsInstance(mock.call_args[0][0], ValueError)
            self.assertEqual(str(mock.call_args[0][0]),
                             "Can't find using both name and hash")

    def test002_files_raise_h_type_None(self):
        self.request.query.hash = "something"
        process_error = "frontend.api.v1_1.controllers.files.process_error"
        with patch(process_error) as mock:
            api_files.list("whatever")
            self.assertTrue(mock.called)
            self.assertIsInstance(mock.call_args[0][0], ValueError)
            self.assertEqual(str(mock.call_args[0][0]), "Hash not supported")
