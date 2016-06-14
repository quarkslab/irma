from unittest import TestCase
from tempfile import TemporaryFile
from mock import MagicMock, patch
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from frontend.models.sqlobjects import File, Tag
from lib.irma.database.sqlobjects import SQLDatabaseObject
from lib.irma.common.exceptions import IrmaDatabaseError, IrmaFileSystemError
from lib.irma.common.exceptions import IrmaDatabaseResultNotFound


class TestFile(TestCase):

    def setUp(self):
        self.sha256 = "sha256"
        self.sha1 = "sha1"
        self.md5 = "md5"
        self.size = 1024
        self.mimetype = "MimeType"
        self.path = "path"
        self.first_ts = 0
        self.last_ts = 1

        self.file = File(self.sha256, self.sha1, self.md5, self.size,
                         self.mimetype, self.path, self.first_ts, self.last_ts)

    def tearDown(self):
        del self.file

    def test001___init__(self):
        self.assertEqual(self.file.timestamp_first_scan, self.first_ts)
        self.assertEqual(self.file.timestamp_last_scan, self.last_ts)
        self.assertEqual(self.file.tags, list())
        self.assertIsInstance(self.file, File)
        self.assertIsInstance(self.file, SQLDatabaseObject)

    def test002_to_json(self):
        expected = {'md5': self.md5,
                    "sha1": self.sha1,
                    "sha256": self.sha256,
                    "size": self.size,
                    "timestamp_first_scan": self.first_ts,
                    "timestamp_last_scan": self.last_ts}
        self.assertEqual(self.file.to_json(), expected)

    def test003_to_json_more_stuff(self):
        base = {"md5": "m_test",
                "sha1": "s_test",
                "sha256": "s256_test",
                "size": "si_test"}
        for key, value in base.items():
            setattr(self.file, key, value)
        base["timestamp_first_scan"] = self.first_ts
        base["timestamp_last_scan"] = self.last_ts
        result = self.file.to_json()
        self.assertEqual(result, base)

    def test004_classmethod_load_from_sha256_raise_NoResultFound(self):
        sample = "test"
        session = MagicMock()
        session.query.side_effect = NoResultFound(sample)
        with self.assertRaises(IrmaDatabaseResultNotFound) as context:
            File.load_from_sha256("whatever", session)
        self.assertEqual(str(context.exception), sample)

    def test005_classmethod_load_from_sha256_raise_MultipleResultNotFound(self):  # nopep8
        sample = "test"
        session = MagicMock()
        session.query.side_effect = MultipleResultsFound(sample)
        with self.assertRaises(IrmaDatabaseError) as context:
            File.load_from_sha256("whatever", session)
        self.assertEqual(str(context.exception), sample)

    def test006_classmethod_load_from_sha256_True(self):
        sha = "sha_test"
        session = MagicMock()
        session.query().filter().one().path = None
        File.sha256 = sha
        result = File.load_from_sha256(sha, session)
        self.assertTrue(session.query.called)
        self.assertEqual(session.query.call_args, ((File,),))
        self.assertTrue(session.query().filter.called)
        self.assertEqual(session.query().filter.call_args, ((True,),))
        self.assertTrue(session.query().filter().one.called)
        self.assertEqual(session.query().filter().one.call_args, (tuple(),))
        self.assertEqual(result, session.query().filter().one())

    def test007_classmethod_load_from_sha256_path_is_None(self):
        sha, data = "sha_test", TemporaryFile()
        session = MagicMock()
        session.query().filter().one().path = None
        File.sha256 = sha
        File.data = data
        result = File.load_from_sha256(sha, session)
        self.assertTrue(session.query.called)
        self.assertEqual(session.query.call_args, ((File,),))
        self.assertTrue(session.query().filter.called)
        self.assertEqual(session.query().filter.call_args, ((True,),))
        self.assertTrue(session.query().filter().one.called)
        self.assertEqual(session.query().filter().one.call_args, (tuple(),))
        self.assertEqual(result, session.query().filter().one())

    def test008_get_file_names_empty(self):
        self.assertEqual(self.file.get_file_names(), list())

    def test009_get_file_names_some(self):
        a, b, c = MagicMock(), MagicMock(), MagicMock()
        a.name, b.name, c.name = str(a), str(b), str(c)
        self.file.files_web = [a, b, c]
        res = self.file.get_file_names()
        self.assertItemsEqual(res, [str(a), str(b), str(c)])

    def test010_remove_old_files(self):
        m_session = MagicMock()
        m_file = MagicMock()
        m_session.query().filter().filter().all.return_value = [m_file]
        res = File.remove_old_files(10, m_session)
        m_file.remove_file_from_fs.assert_called_once()
        self.assertEqual(res, 1)

    def test011_get_tags(self):
        m_tag = MagicMock()
        self.file.tags = [m_tag]
        res = self.file.get_tags()
        self.assertIs(type(res), list)
        self.assertEquals(res, [m_tag.to_json()])

    def test012_add_tag(self):
        text = "whatever"
        t = Tag(text=text)
        m_session = MagicMock()
        m_session.query(Tag).filter().one.return_value = t
        self.assertEqual(len(self.file.tags), 0)
        self.file.add_tag("id", m_session)
        self.assertEqual(len(self.file.tags), 1)
        self.assertItemsEqual(self.file.tags, [t])

    def test013_add_tag_error(self):
        text = "whatever"
        t = Tag(text=text)
        m_session = MagicMock()
        m_session.query(Tag).filter().one.return_value = t
        self.file.add_tag("id", m_session)
        with self.assertRaises(IrmaDatabaseError):
            self.file.add_tag("id", m_session)
        self.assertItemsEqual(self.file.tags, [t])

    def test014_remove_tag(self):
        text = "whatever"
        t = Tag(text=text)
        m_session = MagicMock()
        m_session.query(Tag).filter().one.return_value = t
        self.assertEqual(len(self.file.tags), 0)
        self.file.add_tag("id", m_session)
        self.file.remove_tag("id", m_session)
        self.assertEqual(len(self.file.tags), 0)

    def test015_remove_tag_error(self):
        text = "whatever"
        t = Tag(text=text)
        m_session = MagicMock()
        m_session.query(Tag).filter().one.return_value = t
        with self.assertRaises(IrmaDatabaseError):
            self.file.remove_tag("id", m_session)
        self.assertEqual(len(self.file.tags), 0)

    @patch("frontend.models.sqlobjects.os")
    def test016_remove_file_from_fs_path_none(self, m_os):
        self.file.path = None
        self.file.remove_file_from_fs()
        m_os.remove.assert_not_called()

    @patch("frontend.models.sqlobjects.os")
    def test017_remove_file_from_fs(self, m_os):
        path = "RandomPath"
        self.file.path = path
        self.file.remove_file_from_fs()
        m_os.remove.assert_called_once_with(path)
        self.assertIsNone(self.file.path)

    @patch("frontend.models.sqlobjects.os")
    def test018_remove_file_from_fs_error(self, m_os):
        path = "RandomPath"
        self.file.path = path
        m_os.remove.side_effect = OSError
        with self.assertRaises(IrmaFileSystemError):
            self.file.remove_file_from_fs()

    @patch("frontend.models.sqlobjects.os")
    def test019_load_from_sha256_no_more_exists(self, m_os):
        path = "RandomPath"
        self.file.path = path
        m_os.path.exists.return_value = False
        m_session = MagicMock()
        m_session.query().filter().one.return_value = self.file
        ret_file = File.load_from_sha256("sha256", m_session)
        self.assertEqual(ret_file, self.file)
        self.assertIsNone(self.file.path)
