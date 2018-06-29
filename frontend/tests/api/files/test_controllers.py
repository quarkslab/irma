import hashlib
from random import randint
from unittest import TestCase

from mock import MagicMock, patch

import api.files.controllers as api_files
from irma.common.base.exceptions import IrmaDatabaseResultNotFound


class TestFilesRoutes(TestCase):

    def setUp(self):
        self.db = MagicMock()
        self.session = self.db.session
        self.old_db = api_files.db
        api_files.db = self.db

    def tearDown(self):
        api_files.db = self.old_db
        del self.db

    def test_files_raise_none_None(self):
        name = "whatever"
        hash = "something"
        with self.assertRaises(ValueError) as context:
            api_files.list(name=name, hash=hash)
        self.assertEqual(str(context.exception),
                         "Can't find using both name and hash")

    def test_files_raise_h_type_None(self):
        hash = "something"
        with self.assertRaises(ValueError) as context:
            api_files.list(hash=hash)
        self.assertEqual(str(context.exception),
                         "Hash not supported")

    @patch('api.files.controllers.FileExt')
    def test_files_by_name(self, m_FileExt):
        name = "something"
        api_files.list(name=name)
        m_FileExt.query_find_by_name.assert_called_once_with(name,
                                                             None,
                                                             self.session)

    @patch('api.files.controllers.FileExt')
    def test_files_by_sha256(self, m_FileExt):
        h = hashlib.sha256()
        data = "something".encode("utf-8")
        h.update(data)
        hash_val = h.hexdigest()
        api_files.list(hash=hash_val)
        m_FileExt.query_find_by_hash.assert_called_once_with("sha256",
                                                             hash_val,
                                                             None,
                                                             self.session)

    @patch('api.files.controllers.FileExt')
    def test_files_by_sha1(self, m_FileExt):
        h = hashlib.sha1()
        data = "something".encode("utf-8")
        h.update(data)
        hash_val = h.hexdigest()
        api_files.list(hash=hash_val)
        m_FileExt.query_find_by_hash.assert_called_once_with("sha1",
                                                             hash_val,
                                                             None,
                                                             self.session)

    @patch('api.files.controllers.FileExt')
    def test_files_by_sha256(self, m_FileExt):
        h = hashlib.md5()
        data = "something".encode("utf-8")
        h.update(data)
        hash_val = h.hexdigest()
        api_files.list(hash=hash_val)
        m_FileExt.query_find_by_hash.assert_called_once_with("md5",
                                                             hash_val,
                                                             None,
                                                             self.session)

    @patch('api.files.controllers.FileExt')
    def test_files_all(self, m_FileExt):
        api_files.list()
        m_FileExt.query_find_by_name.assert_called_once_with("",
                                                             None,
                                                             self.session)

    @patch('api.files.controllers.FileExt')
    def test_files_by_tags(self, m_FileExt):
        tag_list = ["tag1", "tag2"]
        api_files.list(tags=tag_list)
        m_FileExt.query_find_by_name.assert_called_once_with("",
                                                             tag_list,
                                                             self.session)

    @patch('api.files.controllers.FileExt')
    def test_files_offset_limit(self, m_FileExt):
        offset = randint(1000, 2000)
        limit = randint(0, 1000)
        api_files.list(offset=offset, limit=limit)
        m_FileExt.query_find_by_name().limit.assert_called_once_with(limit)
        m_offset = m_FileExt.query_find_by_name().limit().offset
        m_offset.assert_called_once_with(offset)

    @patch('api.files.controllers.File')
    @patch('api.files.controllers.FileExt')
    def test_files_get(self, m_FileExt, m_File):
        sha256 = "whatever"
        m_response = MagicMock()
        api_files.get(m_response, sha256)
        m_File.load_from_sha256.assert_called_once_with(sha256,
                                                        self.db.session)
        m_func = m_FileExt.query_find_by_hash
        m_func.assert_called_once_with("sha256", sha256,
                                       None, self.db.session,
                                       distinct_name=False)

    @patch('api.files.controllers.File')
    def test_files_get_error(self, m_File):
        sha256 = "whatever"
        exception = Exception()
        m_File.load_from_sha256.side_effect = exception
        with self.assertRaises(Exception):
            api_files.get(sha256, self.db)

    @patch('api.files.controllers.File')
    @patch('api.files.controllers.FileExt')
    def test_files_get_offset_limit(self, m_FileExt, m_File):
        sha256 = "whatever"
        offset = randint(1000, 2000)
        limit = randint(0, 1000)
        m_response = MagicMock()
        api_files.get(m_response, sha256, offset=offset, limit=limit)
        m_File.load_from_sha256.assert_called_once_with(sha256,
                                                        self.db.session)
        m_query = m_FileExt.query_find_by_hash
        m_query().limit.assert_called_once_with(limit)
        m_query().limit().offset.assert_called_once_with(offset)

    @patch('api.files.controllers.File')
    def test_add_tag(self, m_File):
        sha256 = "whatever"
        tagid = randint(0, 1000)
        m_fobj = MagicMock()
        m_File.load_from_sha256.return_value = m_fobj
        api_files.add_tag(sha256, tagid)
        m_File.load_from_sha256.assert_called_once_with(sha256,
                                                        self.db.session)
        m_fobj.add_tag.assert_called_once_with(tagid, self.db.session)

    @patch('api.files.controllers.File')
    def test_add_tag_error(self, m_File):
        exception = Exception()
        m_File.load_from_sha256.side_effect = exception
        with self.assertRaises(Exception):
            api_files.add_tag(None, None)

    @patch('api.files.controllers.File')
    def test_remove_tag(self, m_File):
        sha256 = "whatever"
        tagid = randint(0, 1000)
        m_fobj = MagicMock()
        m_File.load_from_sha256.return_value = m_fobj
        api_files.remove_tag(sha256, tagid)
        m_File.load_from_sha256.assert_called_once_with(sha256, self.session)
        m_fobj.remove_tag.assert_called_once_with(tagid, self.session)

    @patch('api.files.controllers.File')
    def test_remove_tag_error(self, m_File):
        exception = Exception()
        m_File.load_from_sha256.side_effect = exception
        with self.assertRaises(Exception):
            api_files.remove_tag(None, None)

    @patch('api.files.controllers.open')
    @patch('api.files.controllers.File')
    def test_download(self, m_File, m_open):
        sha256 = "whatever"
        m_response = MagicMock()
        api_files.download(m_response, sha256)
        m_File.load_from_sha256.assert_called_once_with(sha256,
                                                        self.session)

    @patch('api.files.controllers.open')
    @patch('api.files.controllers.File')
    def test_download_deleted_file(self, m_File, m_open):
        sha256 = "whatever"
        m_fobj = MagicMock()
        m_fobj.path = None
        m_File.load_from_sha256.return_value = m_fobj
        with self.assertRaises(IrmaDatabaseResultNotFound) as context:
            api_files.download(sha256, self.db)
        self.assertEqual(str(context.exception), "downloading a removed file")
