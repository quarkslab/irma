import hashlib
from unittest import TestCase
from mock import MagicMock, patch
from bottle import FormsDict

import frontend.api.v1.controllers.search as api_search
from random import randint


class TestApiSearch(TestCase):

    def setUp(self):
        self.old_file_web_schema = api_search.file_web_schema
        self.old_request = api_search.request
        self.file_web_schema = MagicMock()
        self.request = MagicMock()
        self.request.query = FormsDict()
        self.db = MagicMock()
        api_search.file_web_schema = self.file_web_schema
        api_search.request = self.request

    def tearDown(self):
        api_search.file_web_schema = self.old_file_web_schema
        api_search.request = self.old_request
        del self.file_web_schema
        del self.request

    @patch("frontend.api.v1.controllers.search.process_error")
    def test001_files_raise_none_None(self, m_process_error):
        self.request.query['name'] = "whatever"
        self.request.query['hash'] = "something"
        api_search.files(self.db)
        self.assertTrue(m_process_error.called)
        self.assertIsInstance(m_process_error.call_args[0][0], ValueError)
        self.assertEqual(str(m_process_error.call_args[0][0]),
                         "Can't find using both name and hash")

    @patch("frontend.api.v1.controllers.search.process_error")
    def test002_files_raise_h_type_None(self, m_process_error):
        self.request.query['hash'] = "something"
        api_search.files(self.db)
        self.assertTrue(m_process_error.called)
        self.assertIsInstance(m_process_error.call_args[0][0], ValueError)
        self.assertEqual(str(m_process_error.call_args[0][0]),
                         "Hash not supported")

    @patch('frontend.api.v1.controllers.search.FileWeb')
    def test003_files_by_name(self, m_FileWeb):
        name = "something"
        self.request.query['name'] = name
        api_search.files(self.db)
        m_FileWeb.query_find_by_name.assert_called_once_with(name,
                                                             None,
                                                             self.db)

    @patch('frontend.api.v1.controllers.search.FileWeb')
    def test004_files_by_sha256(self, m_FileWeb):
        h = hashlib.sha256()
        h.update("something")
        hash_val = h.hexdigest()
        self.request.query['hash'] = hash_val
        api_search.files(self.db)
        m_FileWeb.query_find_by_hash.assert_called_once_with("sha256",
                                                             hash_val,
                                                             None,
                                                             self.db)

    @patch('frontend.api.v1.controllers.search.FileWeb')
    def test005_files_by_sha1(self, m_FileWeb):
        h = hashlib.sha1()
        h.update("something")
        hash_val = h.hexdigest()
        self.request.query['hash'] = hash_val
        api_search.files(self.db)
        m_FileWeb.query_find_by_hash.assert_called_once_with("sha1",
                                                             hash_val,
                                                             None,
                                                             self.db)

    @patch('frontend.api.v1.controllers.search.FileWeb')
    def test006_files_by_sha256(self, m_FileWeb):
        h = hashlib.md5()
        h.update("something")
        hash_val = h.hexdigest()
        self.request.query['hash'] = hash_val
        api_search.files(self.db)
        m_FileWeb.query_find_by_hash.assert_called_once_with("md5",
                                                             hash_val,
                                                             None,
                                                             self.db)

    @patch('frontend.api.v1.controllers.search.FileWeb')
    def test007_files_all(self, m_FileWeb):
        api_search.files(self.db)
        m_FileWeb.query_find_by_name.assert_called_once_with("",
                                                             None,
                                                             self.db)

    @patch('frontend.api.v1.controllers.search.FileWeb')
    def test008_files_offset_limit(self, m_FileWeb):
        offset = randint(1000, 2000)
        limit = randint(0, 1000)
        self.request.query['offset'] = offset
        self.request.query['limit'] = limit
        api_search.files(self.db)
        m_limit = m_FileWeb.query_find_by_name().limit
        m_limit.assert_called_once_with(limit)
        m_limit().offset.assert_called_once_with(offset)
