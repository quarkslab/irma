from unittest import TestCase
from tempfile import TemporaryFile
from mock import MagicMock, patch
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

import api.files.models as module
from api.tags.models import Tag
from irma.common.base.exceptions import IrmaDatabaseError, IrmaFileSystemError
from irma.common.base.exceptions import IrmaDatabaseResultNotFound


class TestFileModels(TestCase):

    def setUp(self):
        self.sha256 = "sha256"
        self.sha1 = "sha1"
        self.md5 = "md5"
        self.size = 1024
        self.mimetype = "MimeType"
        self.path = "path"
        self.first_ts = 0
        self.last_ts = 1

        self.file = module.File(self.sha256, self.sha1, self.md5, self.size,
                                self.mimetype, self.path, self.first_ts,
                                self.last_ts)

    def tearDown(self):
        del self.file

    def test___init__(self):
        self.assertEqual(self.file.timestamp_first_scan, self.first_ts)
        self.assertEqual(self.file.timestamp_last_scan, self.last_ts)
        self.assertEqual(self.file.tags, list())
        self.assertIsInstance(self.file, module.File)

    def test___init__with_tags(self):
        tags = [module.Tag("tag1"), module.Tag("tag2")]
        file = module.File(self.sha256, self.sha1, self.md5, self.size,
                           self.mimetype, self.path, self.first_ts,
                           self.last_ts, tags=tags)
        self.assertEqual(file.tags, tags)

    def test_classmethod_load_from_sha256_raise_NoResultFound(self):
        sample = "test"
        session = MagicMock()
        session.query.side_effect = NoResultFound(sample)
        with self.assertRaises(IrmaDatabaseResultNotFound) as context:
            module.File.load_from_sha256("whatever", session)
        self.assertEqual(str(context.exception), sample)

    def test_classmethod_load_from_sha256_raise_MultipleResultNotFound(self):  # nopep8
        sample = "test"
        session = MagicMock()
        session.query.side_effect = MultipleResultsFound(sample)
        with self.assertRaises(IrmaDatabaseError) as context:
            module.File.load_from_sha256("whatever", session)
        self.assertEqual(str(context.exception), sample)

    def test_classmethod_load_from_sha256_True(self):
        sha = "sha_test"
        session = MagicMock()
        session.query().filter().one().path = None
        module.File.sha256 = sha
        result = module.File.load_from_sha256(sha, session)
        self.assertTrue(session.query.called)
        self.assertEqual(session.query.call_args, ((module.File,),))
        self.assertTrue(session.query().filter.called)
        self.assertEqual(session.query().filter.call_args, ((True,),))
        self.assertTrue(session.query().filter().one.called)
        self.assertEqual(session.query().filter().one.call_args, (tuple(),))
        self.assertEqual(result, session.query().filter().one())

    def test_classmethod_load_from_sha256_path_is_None(self):
        sha, data = "sha_test", TemporaryFile()
        session = MagicMock()
        session.query().filter().one().path = None
        module.File.sha256 = sha
        module.File.data = data
        result = module.File.load_from_sha256(sha, session)
        self.assertTrue(session.query.called)
        self.assertEqual(session.query.call_args, ((module.File,),))
        self.assertTrue(session.query().filter.called)
        self.assertEqual(session.query().filter.call_args, ((True,),))
        self.assertTrue(session.query().filter().one.called)
        self.assertEqual(session.query().filter().one.call_args, (tuple(),))
        self.assertEqual(result, session.query().filter().one())

    def test_get_file_names_empty(self):
        self.assertEqual(self.file.filenames, list())

    def test_get_file_names_some(self):
        a, b, c = MagicMock(), MagicMock(), MagicMock()
        a.name, b.name, c.name = str(a), str(b), str(c)
        self.file.files_ext = [a, b, c]
        res = self.file.filenames
        self.assertCountEqual(res, [str(a), str(b), str(c)])

    def test_remove_old_files(self):
        m_session = MagicMock()
        m_file = MagicMock()
        m_session.query().filter().filter().all.return_value = [m_file]
        res = module.File.remove_old_files(10, m_session)
        m_file.remove_file_from_fs.assert_called_once()
        self.assertEqual(res, 1)

    def test_get_tags(self):
        m_tag = MagicMock()
        self.file.tags = [m_tag]
        res = self.file.get_tags()
        self.assertIs(type(res), list)
        self.assertEqual(res, [m_tag.to_json()])

    def test_add_tag(self):
        text = "whatever"
        t = Tag(text=text)
        m_session = MagicMock()
        m_session.query(Tag).filter_by().one.return_value = t
        self.assertEqual(len(self.file.tags), 0)
        self.file.add_tag("id", m_session)
        self.assertEqual(len(self.file.tags), 1)
        self.assertCountEqual(self.file.tags, [t])

    def test_add_tag_error(self):
        text = "whatever"
        t = Tag(text=text)
        m_session = MagicMock()
        m_session.query(Tag).filter_by().one.return_value = t
        self.file.add_tag("id", m_session)
        with self.assertRaises(IrmaDatabaseError):
            self.file.add_tag("id", m_session)
        self.assertCountEqual(self.file.tags, [t])

    def test_remove_tag(self):
        text = "whatever"
        t = Tag(text=text)
        m_session = MagicMock()
        m_session.query(Tag).filter().one.return_value = t
        self.assertEqual(len(self.file.tags), 0)
        self.file.add_tag("id", m_session)
        self.file.remove_tag("id", m_session)
        self.assertEqual(len(self.file.tags), 0)

    def test_remove_tag_error(self):
        text = "whatever"
        t = Tag(text=text)
        m_session = MagicMock()
        m_session.query(Tag).filter().one.return_value = t
        with self.assertRaises(IrmaDatabaseError):
            self.file.remove_tag("id", m_session)
        self.assertEqual(len(self.file.tags), 0)

    @patch("api.files.models.os")
    def test_remove_file_from_fs_path_none(self, m_os):
        self.file.path = None
        self.file.remove_file_from_fs()
        m_os.remove.assert_not_called()

    @patch("api.files.models.os")
    def test_remove_file_from_fs(self, m_os):
        path = "RandomPath"
        self.file.path = path
        self.file.remove_file_from_fs()
        m_os.remove.assert_called_once_with(path)
        self.assertIsNone(self.file.path)

    @patch("api.files.models.os")
    def test_remove_file_from_fs_error(self, m_os):
        path = "RandomPath"
        self.file.path = path
        m_os.remove.side_effect = OSError
        self.file.remove_file_from_fs()
        self.assertIsNone(self.file.path)

    def test_remove_old_files(self):
        f1, f2 = MagicMock(), MagicMock()
        session = MagicMock()
        session.query().filter().filter().all.return_value = [f1, f2]
        res = module.File.remove_old_files(10, session)
        self.assertEqual(res, 2)
        f1.remove_file_from_fs.assert_called_once()
        f2.remove_file_from_fs.assert_called_once()

    def test_remove_files_max_size(self):
        f1, f2 = MagicMock(), MagicMock()
        session = MagicMock()
        session.query().filter().subquery().c.total = 50
        session.query().filter().all.return_value = [f1, f2]
        res = module.File.remove_files_max_size(10, session)
        self.assertEqual(res, 2)
        f1.remove_file_from_fs.assert_called_once()
        f2.remove_file_from_fs.assert_called_once()

    @patch("api.files.models.os")
    def test_load_from_sha256_no_more_exists(self, m_os):
        path = "RandomPath"
        self.file.path = path
        m_os.path.exists.return_value = False
        m_session = MagicMock()
        m_session.query().filter().one.return_value = self.file
        ret_file = module.File.load_from_sha256("sha256", m_session)
        self.assertEqual(ret_file, self.file)
        self.assertIsNone(self.file.path)

    @patch("api.files.models.os")
    @patch("api.files.models.save_to_file")
    @patch("api.files.models.build_sha256_path")
    @patch("api.files.models.sha256sum")
    def test_new_file_existing(self, m_sha256sum, m_build_sha256_path,
                               m_save_to_file, m_os):
        m_file = MagicMock()
        fobj = MagicMock()
        m_file.path = "filepath"
        sha256val = "whatever"
        m_os.path.exists(m_file.path).return_value = True
        m_sha256sum.return_value = sha256val
        m_session = MagicMock()
        m_session.query(module.File).filter(
            module.File.sha256 == sha256val
        ).one.return_value = m_file
        m_file.path = "whatever"
        res = module.File.get_or_create(fobj, m_session)
        m_build_sha256_path.assert_called()
        m_save_to_file.assert_not_called()
        self.assertEqual(res, m_file)

    @patch("api.files.models.os")
    @patch("api.files.models.save_to_file")
    @patch("api.files.models.build_sha256_path")
    @patch("api.files.models.sha256sum")
    def test_new_file_existing_deleted(self, m_sha256sum, m_build_sha256_path,
                                       m_save_to_file, m_os):
        m_file = MagicMock()
        fobj = MagicMock()
        m_file.path = "filepath"
        sha256val = "whatever"
        m_os.path.exists(m_file.path).return_value = False
        m_sha256sum.return_value = sha256val
        m_session = MagicMock()
        m_session.query(module.File).filter(
                module.File.sha256 == sha256val
        ).one.return_value = m_file
        m_file.path = None
        res = module.File.get_or_create(fobj, m_session)
        m_build_sha256_path.assert_called()
        m_save_to_file.assert_called()
        self.assertEqual(res, m_file)

    @patch("api.files.models.md5sum")
    @patch("api.files.models.sha1sum")
    @patch("api.files.models.sha256sum")
    @patch("api.files.models.Magic")
    @patch("api.files.models.save_to_file")
    @patch("api.files.models.build_sha256_path")
    def test_new_file_not_existing(self, m_build_sha256_path,
                                   m_save_to_file, m_magic,
                                   m_sha256sum, m_sha1sum, m_md5sum):
        sha256val = "whatever"
        m_sha256sum.return_value = sha256val

        m_session = MagicMock()
        m_session.query(module.File).filter(
                module.File.sha256 == sha256val
        ).one.side_effect = IrmaDatabaseResultNotFound
        fobj = MagicMock()
        path = "/a/absolute/path/to/testpath"
        m_build_sha256_path.return_value = path
        module.File.get_or_create(fobj, m_session)
        m_md5sum.assert_called_once_with(fobj)
        m_sha1sum.assert_called_once_with(fobj)
        m_sha256sum.assert_called_once_with(fobj)
        m_save_to_file.assert_called_with(fobj, path)
        m_magic.assert_called()

    @patch("api.files.models.md5sum")
    @patch("api.files.models.sha1sum")
    @patch("api.files.models.sha256sum")
    @patch("api.files.models.Magic")
    @patch("api.files.models.save_to_file")
    @patch("api.files.models.build_sha256_path")
    def test_new_file_race_integrity_error(self, m_build_sha256_path,
                                           m_save_to_file, m_magic,
                                           m_sha256sum, m_sha1sum, m_md5sum):
        sha256val = "whatever"
        m_sha256sum.return_value = sha256val

        m_session = MagicMock()
        m_session.query(module.File).filter(
                module.File.sha256 == sha256val
        ).one.side_effect = IrmaDatabaseResultNotFound
        stmt, params, orig = MagicMock(), MagicMock(), MagicMock()
        m_session.add.side_effect = module.IntegrityError(stmt, params, orig)
        fobj = MagicMock()
        path = "/a/absolute/path/to/testpath"
        m_build_sha256_path.return_value = path
        with self.assertRaises(module.IrmaDatabaseError):
            module.File.get_or_create(fobj, m_session)
        m_md5sum.assert_called_once_with(fobj)
        m_sha1sum.assert_called_once_with(fobj)
        m_sha256sum.assert_called_once_with(fobj)
        m_save_to_file.assert_called_with(fobj, path)
        m_magic.assert_called()

    @patch("api.files.models.inspect")
    def test_get_ref_result(self, m_inspect):
        m_session = MagicMock()
        m_inspect(self.file).session = m_session
        probename = "probeX"
        res = self.file.get_ref_result(probename)
        expected = m_session.query().join().filter().\
            filter(module.ProbeResult.name == probename).\
            order_by().\
            first()
        self.assertEqual(res, expected)
