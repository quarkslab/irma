from unittest import TestCase
from random import randint
from mock import MagicMock, patch
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from frontend.models.sqlobjects import FileWeb
from lib.irma.common.exceptions import IrmaDatabaseError
from lib.irma.common.exceptions import IrmaDatabaseResultNotFound
from lib.irma.common.utils import IrmaProbeType


class TestFileWeb(TestCase):

    def setUp(self):
        self.file = MagicMock()
        self.name = "name"
        self.path = "path"
        self.scan = MagicMock()
        self.fw = FileWeb(self.file, self.name, self.path, self.scan)

    def tearDown(self):
        del self.fw

    def test001_load_from_ext_id(self):
        m_session = MagicMock()
        ext_id = "whatever"
        FileWeb.load_from_ext_id(ext_id, m_session)
        m_filter = m_session.query(FileWeb).filter
        m_filter.is_called_once_with(FileWeb.external_id == ext_id)

    def test002_load_from_ext_id_raises(self):
        m_session = MagicMock()
        ext_id = "whatever"
        m_session.query.side_effect = NoResultFound()
        with self.assertRaises(IrmaDatabaseResultNotFound):
            FileWeb.load_from_ext_id(ext_id, m_session)

    def test003_load_from_ext_id_raises(self):
        m_session = MagicMock()
        ext_id = "whatever"
        m_session.query.side_effect = MultipleResultsFound()
        with self.assertRaises(IrmaDatabaseError):
            FileWeb.load_from_ext_id(ext_id, m_session)

    def test004_load_by_scanid(self):
        m_session = MagicMock()
        scanid = "scanid"
        fileid = "fileid"
        FileWeb.load_by_scanid_fileid(scanid, fileid, m_session)
        m_filter = m_session.query(FileWeb).filter
        m_filter.is_called_once_with(FileWeb.id_scan == scanid,
                                     FileWeb.id_file == fileid)

    def test005_load_by_scanid_raises(self):
        m_session = MagicMock()
        m_session.query.side_effect = NoResultFound()
        with self.assertRaises(IrmaDatabaseError):
            FileWeb.load_by_scanid_fileid(None, None, m_session)

    @patch("frontend.models.sqlobjects.File")
    @patch("frontend.models.sqlobjects.Tag")
    def test006_find_by_name(self, m_Tag, m_File):
        m_session = MagicMock()
        name = "something"
        tag = MagicMock()
        tag.id = randint(0, 10)
        tags = [tag.id]
        FileWeb.query_find_by_name(name, tags, m_session)
        m_Tag.find_by_id.assert_called_once_with(tag.id, m_session)

    @patch("frontend.models.sqlobjects.File")
    @patch("frontend.models.sqlobjects.Tag")
    def test007_find_by_hash(self, m_Tag, m_File):
        m_session = MagicMock()
        hash_type, hash = "something", "anotherthing"
        tag = MagicMock()
        tag.id = randint(0, 10)
        tags = [tag.id]
        FileWeb.query_find_by_hash(hash_type, hash, tags, m_session)
        m_session.query.called_with(FileWeb)
        m_Tag.find_by_id.assert_called_once_with(tag.id, m_session)

    @patch("frontend.models.sqlobjects.File")
    @patch("frontend.models.sqlobjects.Tag")
    def test007_find_by_hash_distinct_false(self, m_Tag, m_File):
        m_session = MagicMock()
        hash_type, hash = "something", "anotherthing"
        tag = MagicMock()
        tag.id = randint(0, 10)
        tags = [tag.id]
        FileWeb.query_find_by_hash(hash_type, hash, tags, m_session,
                                   distinct_name=False)
        m_session.query.called_with(FileWeb)
        m_Tag.find_by_id.assert_called_once_with(tag.id, m_session)

    def test008_probes_finished(self):
        pr1, pr2 = MagicMock(), MagicMock()
        pr1.doc = None
        pr2.doc = "whatever"
        self.fw.probe_results = [pr1, pr2]
        self.assertEqual(self.fw.probes_finished, 1)

    def test009_probes_finished_all_none(self):
        pr1, pr2 = MagicMock(), MagicMock()
        pr1.doc = None
        pr2.doc = None
        self.fw.probe_results = [pr1, pr2]
        self.assertEqual(self.fw.probes_finished, 0)

    def test010_status_0(self):
        pr1, pr2 = MagicMock(), MagicMock()
        pr1.doc = {'type': IrmaProbeType.antivirus, 'status': 0}
        pr2.doc = {'type': IrmaProbeType.antivirus, 'status': 0}
        self.fw.probe_results = [pr1, pr2]
        self.assertEqual(self.fw.status, 0)

    def test010_status_1(self):
        pr1, pr2 = MagicMock(), MagicMock()
        pr1.doc = {'type': IrmaProbeType.antivirus, 'status': 0}
        pr2.doc = {'type': IrmaProbeType.antivirus, 'status': 1}
        self.fw.probe_results = [pr1, pr2]
        self.assertEqual(self.fw.status, 1)

    def test011_get_probe_results(self):
        pr1, pr2 = MagicMock(), MagicMock()
        pr1.doc = "whatever"
        pr2.doc = "something"
        self.fw.probe_results = [pr1, pr2]
        self.assertItemsEqual(self.fw.get_probe_results(),
                              [pr1.get_details(True),
                               pr2.get_details(True)])
        pr1.get_details.assert_called_with(True)
        pr2.get_details.assert_called_with(True)
