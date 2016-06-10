from unittest import TestCase
from tempfile import TemporaryFile
from random import choice, randint
from mock import MagicMock, patch
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from frontend.models.sqlobjects import File, ProbeResult, Scan, FileWeb
from lib.irma.database.sqlobjects import SQLDatabaseObject
from lib.irma.common.utils import IrmaScanStatus
from lib.irma.common.exceptions import IrmaDatabaseError, IrmaCoreError
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
        result = File.load_from_sha256(sha, session, data)
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


class TestProbeResult(TestCase):

    def setUp(self):
        self.type = "type"
        self.name = "name"
        self.doc = MagicMock()
        self.status = 1
        self.file_web = MagicMock()
        self.proberesult = ProbeResult(self.type, self.name, self.doc,
                                       self.status, self.file_web)

    def tearDown(self):
        del self.proberesult

    @patch("frontend.models.sqlobjects.IrmaFormatter")
    def test012_get_details_formatted(self, m_IrmaFormatter):
        self.proberesult.get_details()
        m_IrmaFormatter.format.assert_called_once()
        self.assertEqual(m_IrmaFormatter.format.call_args[0][0],
                         self.name)

    @patch("frontend.models.sqlobjects.IrmaFormatter")
    def test013_get_details_not_formatted(self, m_IrmaFormatter):
        self.proberesult.get_details(formatted=False)
        m_IrmaFormatter.format.assert_not_called


class TestScan(TestCase):

    def setUp(self):
        self.date = "date"
        self.ip = "ip"
        self.scan = Scan(self.date, self.ip)

    def tearDown(self):
        del self.scan

    def test014_scan_finished_not_uploaded(self):
        status = choice([IrmaScanStatus.empty,
                         IrmaScanStatus.ready])
        self.scan.set_status(status)
        self.assertFalse(self.scan.finished())

    def test015_scan_finished_launched_not_finished(self):
        a, b = MagicMock(), MagicMock()
        a.doc = "something"
        b.doc = None
        fw = MagicMock()
        fw.probe_results = [a, b]
        self.scan.files_web = [fw]
        self.scan.set_status(IrmaScanStatus.launched)
        self.assertFalse(self.scan.finished())

    def test016_scan_finished_launched_finished(self):
        a, b = MagicMock(), MagicMock()
        a.doc = "something"
        b.doc = "anotherthing"
        fw = MagicMock()
        fw.probe_results = [a, b]
        self.scan.files_web = [fw]
        self.scan.set_status(IrmaScanStatus.launched)
        self.assertTrue(self.scan.finished())

    def test017_scan_finished_finished(self):
        self.scan.set_status(IrmaScanStatus.launched)
        res = self.scan.finished()
        self.assertTrue(res)

    def test018_scan_probes_total(self):
        fw1, fw2 = MagicMock(), MagicMock()
        pt1, pt2 = randint(0, 20), randint(0, 20)
        fw1.probes_total = pt1
        fw2.probes_total = pt2
        self.scan.files_web = [fw1, fw2]
        self.assertEquals(self.scan.probes_total, pt1 + pt2)

    def test019_scan_probes_finished(self):
        fw1, fw2 = MagicMock(), MagicMock()
        pf1, pf2 = randint(0, 20), randint(0, 20)
        fw1.probes_finished = pf1
        fw2.probes_finished = pf2
        self.scan.files_web = [fw1, fw2]
        self.assertEquals(self.scan.probes_finished, pf1 + pf2)

    def test020_scan_files(self):
        fw = MagicMock()
        self.scan.files_web = [fw]
        self.assertEqual(self.scan.files, [fw.file])

    def test021_scan_set_status(self):
        with self.assertRaises(IrmaCoreError):
            self.scan.set_status("whatever")

    def test022_scan_get_fileweb_by_sha256(self):
        fw = MagicMock()
        sha256 = "whatever"
        fw.file.sha256 = sha256
        self.scan.files_web = [fw]
        self.assertEqual(self.scan.get_filewebs_by_sha256(sha256), [fw])

    def test023_scan_query_find_by_filesha256(self):
        m_session = MagicMock()
        sha256 = "whatever"
        Scan.query_find_by_filesha256(sha256, m_session)
        m_filter = m_session.query(Scan).join().join().filter
        m_filter.is_called_once_with(File.sha256 == sha256)


class TestFileWeb(TestCase):

    def test024_fileweb_load_from_ext_id(self):
        m_session = MagicMock()
        ext_id = "whatever"
        FileWeb.load_from_ext_id(ext_id, m_session)
        m_filter = m_session.query(FileWeb).filter
        m_filter.is_called_once_with(FileWeb.external_id == ext_id)

    def test025_fileweb_load_from_ext_id_raises(self):
        m_session = MagicMock()
        ext_id = "whatever"
        m_session.query.side_effect = NoResultFound()
        with self.assertRaises(IrmaDatabaseResultNotFound):
            FileWeb.load_from_ext_id(ext_id, m_session)

    def test026_fileweb_load_from_ext_id_raises(self):
        m_session = MagicMock()
        ext_id = "whatever"
        m_session.query.side_effect = MultipleResultsFound()
        with self.assertRaises(IrmaDatabaseError):
            FileWeb.load_from_ext_id(ext_id, m_session)

    def test027_fileweb_load_by_scanid(self):
        m_session = MagicMock()
        scanid = "scanid"
        fileid = "fileid"
        FileWeb.load_by_scanid_fileid(scanid, fileid, m_session)
        m_filter = m_session.query(FileWeb).filter
        m_filter.is_called_once_with(FileWeb.id_scan == scanid,
                                     FileWeb.id_file == fileid)

    def test028_fileweb_load_by_scanid_raises(self):
        m_session = MagicMock()
        m_session.query.side_effect = NoResultFound()
        with self.assertRaises(IrmaDatabaseError):
            FileWeb.load_by_scanid_fileid(None, None, m_session)

    @patch("frontend.models.sqlobjects.File")
    @patch("frontend.models.sqlobjects.Tag")
    def test029_fileweb_find_by_name(self, m_Tag, m_File):
        m_session = MagicMock()
        name = "something"
        tag = MagicMock()
        tag.id = randint(0, 10)
        tags = [tag.id]
        FileWeb.query_find_by_name(name, tags, m_session)
        m_Tag.find_by_id.assert_called_once_with(tag.id, m_session)

    @patch("frontend.models.sqlobjects.File")
    @patch("frontend.models.sqlobjects.Tag")
    def test029_fileweb_find_by_hash(self, m_Tag, m_File):
        m_session = MagicMock()
        hash_type, hash = "something", "anotherthing"
        tag = MagicMock()
        tag.id = randint(0, 10)
        tags = [tag.id]
        FileWeb.query_find_by_hash(hash_type, hash, tags, m_session)
        m_Tag.find_by_id.assert_called_once_with(tag.id, m_session)
