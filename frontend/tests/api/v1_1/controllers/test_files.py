import hashlib
from unittest import TestCase
from mock import MagicMock, patch
from random import randint

import frontend.api.v1_1.controllers.files as api_files
from bottle import FormsDict
from lib.irma.common.exceptions import IrmaDatabaseResultNotFound


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

    @patch("frontend.api.v1_1.controllers.files.process_error")
    def test001_files_raise_none_None(self, m_process_error):
        self.request.query['name'] = "whatever"
        self.request.query.hash = "something"
        api_files.list(self.db)
        self.assertTrue(m_process_error.called)
        self.assertIsInstance(m_process_error.call_args[0][0], ValueError)
        self.assertEqual(str(m_process_error.call_args[0][0]),
                         "Can't find using both name and hash")

    @patch("frontend.api.v1_1.controllers.files.process_error")
    def test002_files_raise_h_type_None(self, m_process_error):
        self.request.query['hash'] = "something"
        api_files.list(self.db)
        self.assertTrue(m_process_error.called)
        self.assertIsInstance(m_process_error.call_args[0][0], ValueError)
        self.assertEqual(str(m_process_error.call_args[0][0]),
                         "Hash not supported")

    @patch('frontend.api.v1_1.controllers.files.FileWeb')
    def test003_files_by_name(self, m_FileWeb):
        name = "something"
        self.request.query['name'] = name
        api_files.list(self.db)
        m_FileWeb.query_find_by_name.assert_called_once_with(name,
                                                             None,
                                                             self.db)

    @patch('frontend.api.v1_1.controllers.files.FileWeb')
    def test004_files_by_sha256(self, m_FileWeb):
        h = hashlib.sha256()
        h.update("something")
        hash_val = h.hexdigest()
        self.request.query['hash'] = hash_val
        api_files.list(self.db)
        m_FileWeb.query_find_by_hash.assert_called_once_with("sha256",
                                                             hash_val,
                                                             None,
                                                             self.db)

    @patch('frontend.api.v1_1.controllers.files.FileWeb')
    def test005_files_by_sha1(self, m_FileWeb):
        h = hashlib.sha1()
        h.update("something")
        hash_val = h.hexdigest()
        self.request.query['hash'] = hash_val
        api_files.list(self.db)
        m_FileWeb.query_find_by_hash.assert_called_once_with("sha1",
                                                             hash_val,
                                                             None,
                                                             self.db)

    @patch('frontend.api.v1_1.controllers.files.FileWeb')
    def test006_files_by_sha256(self, m_FileWeb):
        h = hashlib.md5()
        h.update("something")
        hash_val = h.hexdigest()
        self.request.query['hash'] = hash_val
        api_files.list(self.db)
        m_FileWeb.query_find_by_hash.assert_called_once_with("md5",
                                                             hash_val,
                                                             None,
                                                             self.db)

    @patch('frontend.api.v1_1.controllers.files.FileWeb')
    def test007_files_all(self, m_FileWeb):
        api_files.list(self.db)
        m_FileWeb.query_find_by_name.assert_called_once_with("",
                                                             None,
                                                             self.db)

    @patch('frontend.api.v1_1.controllers.files.FileWeb')
    def test007_files_by_tags(self, m_FileWeb):
        tag_list = ["tag1", "tag2"]
        self.request.query['tags'] = ",".join(tag_list)
        api_files.list(self.db)
        m_FileWeb.query_find_by_name.assert_called_once_with("",
                                                             tag_list,
                                                             self.db)

    @patch('frontend.api.v1_1.controllers.files.FileWeb')
    def test008_files_offset_limit(self, m_FileWeb):
        offset = randint(1000, 2000)
        limit = randint(0, 1000)
        self.request.query['offset'] = offset
        self.request.query['limit'] = limit
        api_files.list(self.db)
        m_FileWeb.query_find_by_name().limit.assert_called_once_with(limit)
        m_offset = m_FileWeb.query_find_by_name().limit().offset
        m_offset.assert_called_once_with(offset)

    @patch('frontend.api.v1_1.controllers.files.File')
    @patch('frontend.api.v1_1.controllers.files.FileWeb')
    @patch('frontend.api.v1_1.controllers.files.FileWebSchema_v1_1')
    @patch('frontend.api.v1_1.controllers.files.FileSchema_v1_1')
    def test009_files_get(self, m_FileSchema, m_FileWebSchema,
                          m_FileWeb, m_File):
        sha256 = "whatever"
        api_files.get(sha256, self.db)
        m_File.load_from_sha256.assert_called_once_with(sha256, self.db)
        m_func = m_FileWeb.query_find_by_hash
        m_func.assert_called_once_with("sha256", sha256,
                                       None, self.db, distinct_name=False)

    @patch('frontend.api.v1_1.controllers.files.process_error')
    @patch('frontend.api.v1_1.controllers.files.File')
    def test010_files_get_error(self, m_File, m_process_error):
        sha256 = "whatever"
        exception = Exception()
        m_File.load_from_sha256.side_effect = exception
        api_files.get(sha256, self.db)
        m_process_error.assert_called_with(exception)

    @patch('frontend.api.v1_1.controllers.files.File')
    @patch('frontend.api.v1_1.controllers.files.FileWeb')
    @patch('frontend.api.v1_1.controllers.files.FileWebSchema_v1_1')
    @patch('frontend.api.v1_1.controllers.files.FileSchema_v1_1')
    def test011_files_get_offset_limit(self, m_FileSchema, m_FileWebSchema,
                                       m_FileWeb, m_File):
        sha256 = "whatever"
        offset = randint(1000, 2000)
        limit = randint(0, 1000)
        self.request.query['offset'] = offset
        self.request.query['limit'] = limit
        api_files.get(sha256, self.db)
        m_File.load_from_sha256.assert_called_once_with(sha256, self.db)
        m_query = m_FileWeb.query_find_by_hash
        m_query().limit.assert_called_once_with(limit)
        m_query().limit().offset.assert_called_once_with(offset)

    @patch('frontend.api.v1_1.controllers.files.File')
    def test012_add_tag(self, m_File):
        sha256 = "whatever"
        tagid = randint(0, 1000)
        m_fobj = MagicMock()
        m_File.load_from_sha256.return_value = m_fobj
        api_files.add_tag(sha256, tagid, self.db)
        m_File.load_from_sha256.assert_called_once_with(sha256, self.db)
        m_fobj.add_tag.assert_called_once_with(tagid, self.db)

    @patch('frontend.api.v1_1.controllers.files.process_error')
    @patch('frontend.api.v1_1.controllers.files.File')
    def test013_add_tag_error(self, m_File, m_process_error):
        exception = Exception()
        m_File.load_from_sha256.side_effect = exception
        api_files.add_tag(None, None, self.db)
        m_process_error.assert_called_with(exception)

    @patch('frontend.api.v1_1.controllers.files.File')
    def test014_remove_tag(self, m_File):
        sha256 = "whatever"
        tagid = randint(0, 1000)
        m_fobj = MagicMock()
        m_File.load_from_sha256.return_value = m_fobj
        api_files.remove_tag(sha256, tagid, self.db)
        m_File.load_from_sha256.assert_called_once_with(sha256, self.db)
        m_fobj.remove_tag.assert_called_once_with(tagid, self.db)

    @patch('frontend.api.v1_1.controllers.files.process_error')
    @patch('frontend.api.v1_1.controllers.files.File')
    def test015_remove_tag_error(self, m_File, m_process_error):
        exception = Exception()
        m_File.load_from_sha256.side_effect = exception
        api_files.remove_tag(None, None, self.db)
        m_process_error.assert_called_with(exception)

    @patch('frontend.api.v1_1.controllers.files.open')
    @patch('frontend.api.v1_1.controllers.files.File')
    def test016_download(self, m_File, m_open):
        sha256 = "whatever"
        self.request.query['alt'] = "media"
        api_files.get(sha256, self.db)
        m_File.load_from_sha256.assert_called_once_with(sha256, self.db)

    @patch('frontend.api.v1_1.controllers.files.open')
    @patch('frontend.api.v1_1.controllers.files.File')
    def test016_download_deleted_file(self, m_File, m_open):
        sha256 = "whatever"
        m_fobj = MagicMock()
        m_fobj.path = None
        m_File.load_from_sha256.return_value = m_fobj
        with self.assertRaises(IrmaDatabaseResultNotFound) as context:
            api_files._download(sha256, self.db)
        self.assertEqual(str(context.exception), "downloading a removed file")
