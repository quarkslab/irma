import io
from unittest import TestCase

from mock import MagicMock, PropertyMock, patch

import api.files_ext.controllers as api_files_ext
from api.files_ext.models import FileExt
from api.files_ext.schemas import FileExtSchema


class TestFilesExtRoutes(TestCase):

    def assertIsFileExt(self, data):
        self.assertTrue(type(data) == dict)
        self.assertCountEqual(data.keys(), FileExtSchema().fields)

    def assertIsFileExtList(self, data):
        self.assertTrue(type(data) == list)
        for file_ext in data:
            self.assertIsFileExt(file_ext)

    def setUp(self):
        self.db = MagicMock()
        self.session = self.db.session
        self.old_db = api_files_ext.db
        api_files_ext.db = self.db

    def tearDown(self):
        api_files_ext.db = self.old_db
        del self.db

    @patch("api.files_ext.controllers.FileExt")
    def test_get_ok(self, m_FileExt):
        api_version = 1
        resultid = "whatever"
        m_file = MagicMock()
        m_fw = FileExt(m_file, "filename")
        m_FileExt.load_from_ext_id.return_value = m_fw

        # As FileExt.other_results value is normally retrieve from database,
        # when requesting it, the API will not return it, and will break the
        # test.
        # A solution is to patch the property as mentionned in the
        # documentation:
        # (https://docs.python.org/3/library/unittest.mock.html#unittest.mock.PropertyMock)
        # Mocking the type object other_results property will break other tests
        # (the database one) as it will globally mocking it.
        with patch('api.files_ext.models.FileExt.other_results',
                   new_callable=PropertyMock) as m_other_results:
            m_other_results.return_value = [m_fw]
            result = api_files_ext.get(api_version, resultid)

        m_FileExt.load_from_ext_id.assert_called_once_with(resultid,
                                                           self.session)
        self.assertIsFileExt(result)

    @patch("api.files_ext.controllers.FileExt")
    def test_get_formatted_false(self, m_FileExt):
        resultid = "whatever"
        api_version = 1
        m_file_ext = MagicMock()
        m_file_ext.submitter = "webui"
        m_FileExt.load_from_ext_id.return_value = m_file_ext
        ret = api_files_ext.get(api_version, resultid, formatted="no")
        m_FileExt.load_from_ext_id.assert_called_once_with(resultid,
                                                           self.session)
        self.assertIsFileExt(ret)

    @patch("api.files_ext.controllers.FileExt")
    def test_get_error(self, m_FileExt):
        api_version = 1
        resultid = "whatever"
        exception = ValueError()
        m_FileExt.load_from_ext_id.side_effect = exception
        with self.assertRaises(ValueError):
            api_files_ext.get(api_version, resultid)

    @patch("api.files_ext.controllers.File")
    def test_create_ok(self, m_File):
        m_file = MagicMock()
        m_request = MagicMock()
        data = b"DATA"
        filename = "filename"
        m_file.filename = filename
        m_file.file = io.BytesIO(data)
        m_request._params = {'files': m_file,
                             'json': '{"submitter": "cli",'
                             '"submitter_id": "undefined"}'}
        m_file_obj = MagicMock()
        m_File.get_or_create.return_value = m_file_obj
        api_files_ext.create(m_request)

    @patch("api.files_ext.controllers.FileExt")
    def test_add_files_no_file(self, m_FileExt):
        m_request = MagicMock()
        m_request._params['files'] = None
        expected = "The \"files\" parameter is invalid. Empty list"
        with self.assertRaises(api_files_ext.HTTPInvalidParam) as context:
            api_files_ext.create(m_request)
        self.assertEqual(context.exception.description, expected)
        m_FileExt.assert_not_called()

    @patch("api.files.controllers.FileExt")
    def test_add_files_more_than_one_files(self, m_FileExt):
        m_request = MagicMock()
        m_request._params = {'files': ['file1', 'file2']}
        expected = "The \"files\" parameter is invalid. " \
                   "Only one file at a time"
        with self.assertRaises(api_files_ext.HTTPInvalidParam) as context:
            api_files_ext.create(m_request)
        self.assertEqual(context.exception.description, expected)
        m_FileExt.assert_not_called()
