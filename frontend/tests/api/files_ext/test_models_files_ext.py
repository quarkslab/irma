import os
from unittest import TestCase
from random import randint
from mock import MagicMock, patch
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from api.files_ext.models import FileExt
from irma.common.base.exceptions import IrmaDatabaseError
from irma.common.base.exceptions import IrmaDatabaseResultNotFound
from irma.common.base.utils import IrmaProbeType


class TestFileExt(TestCase):

    def setUp(self):
        self.file = MagicMock()
        self.name = "name"
        self.scan = MagicMock()
        self.fw = FileExt(self.file, self.name)

    def tearDown(self):
        del self.fw

    def test_load_from_ext_id(self):
        m_session = MagicMock()
        ext_id = "whatever"
        FileExt.load_from_ext_id(ext_id, m_session)
        m_filter = m_session.query(FileExt).filter
        m_filter.is_called_once_with(FileExt.external_id == ext_id)

    def test_load_from_ext_id_raises(self):
        m_session = MagicMock()
        ext_id = "whatever"
        m_session.query.side_effect = NoResultFound()
        with self.assertRaises(IrmaDatabaseResultNotFound):
            FileExt.load_from_ext_id(ext_id, m_session)

    def test_load_from_ext_id_raises(self):
        m_session = MagicMock()
        ext_id = "whatever"
        m_session.query.side_effect = MultipleResultsFound()
        with self.assertRaises(IrmaDatabaseError):
            FileExt.load_from_ext_id(ext_id, m_session)

    @patch("api.files_ext.models.File")
    @patch("api.files_ext.models.Tag")
    def test_find_by_name(self, m_Tag, m_File):
        m_session = MagicMock()
        name = "something"
        tag = MagicMock()
        tag.id = randint(0, 10)
        tags = [tag.id]
        FileExt.query_find_by_name(name, tags, m_session)
        m_session.query.called_with(m_Tag)
        m_session.query().filter_by.assert_called_once_with(id=tag.id)
        m_session.query().filter_by().one.assert_called_once()

    @patch("api.files_ext.models.File")
    @patch("api.files_ext.models.Tag")
    def test_find_by_hash(self, m_Tag, m_File):
        m_session = MagicMock()
        hash_type, hash = "something", "anotherthing"
        tag = MagicMock()
        tag.id = randint(0, 10)
        tags = [tag.id]
        FileExt.query_find_by_hash(hash_type, hash, tags, m_session)
        m_session.query.called_with(FileExt)
        m_session.query().filter_by.assert_called_once_with(id=tag.id)
        m_session.query().filter_by().one.assert_called_once()

    @patch("api.files_ext.models.File")
    @patch("api.files_ext.models.Tag")
    def test_find_by_hash_distinct_false(self, m_Tag, m_File):
        m_session = MagicMock()
        hash_type, hash = "something", "anotherthing"
        tag = MagicMock()
        tag.id = randint(0, 10)
        tags = [tag.id]
        FileExt.query_find_by_hash(hash_type, hash, tags, m_session,
                                   distinct_name=False)
        m_session.query.called_with(FileExt)
        m_session.query().filter_by.assert_called_once_with(id=tag.id)
        m_session.query().filter_by().one.assert_called_once()

    def test_probes_finished(self):
        pr1, pr2 = MagicMock(), MagicMock()
        pr1.doc = None
        pr2.doc = "whatever"
        self.fw.probe_results = [pr1, pr2]
        self.assertEqual(self.fw.probes_finished, 1)

    def test_probes_finished_all_none(self):
        pr1, pr2 = MagicMock(), MagicMock()
        pr1.doc = None
        pr2.doc = None
        self.fw.probe_results = [pr1, pr2]
        self.assertEqual(self.fw.probes_finished, 0)

    def test_status_0(self):
        pr1, pr2 = MagicMock(), MagicMock()
        pr1.doc = {'type': IrmaProbeType.antivirus, 'status': 0}
        pr2.doc = {'type': IrmaProbeType.antivirus, 'status': 0}
        self.fw.probe_results = [pr1, pr2]
        self.assertEqual(self.fw.status, 0)

    def test_status_1(self):
        pr1, pr2 = MagicMock(), MagicMock()
        pr1.doc = {'type': IrmaProbeType.antivirus, 'status': 0}
        pr2.doc = {'type': IrmaProbeType.antivirus, 'status': 1}
        self.fw.probe_results = [pr1, pr2]
        self.assertEqual(self.fw.status, 1)

    def test_get_probe_results_as_list(self):
        pr1, pr2 = MagicMock(), MagicMock()
        pr1.doc = "whatever"
        pr2.doc = "something"
        self.fw.probe_results = [pr1, pr2]
        self.assertCountEqual(self.fw.get_probe_results(results_as="list"),
                              [pr1.get_details(True),
                               pr2.get_details(True)])
        pr1.get_details.assert_called_with(True)
        pr2.get_details.assert_called_with(True)

    def test_get_probe_results_as_dict(self):
        pr1, pr2 = MagicMock(), MagicMock()
        pr1.doc = "whatever"
        pr2.doc = "something"
        self.fw.probe_results = [pr1, pr2]
        self.assertIsInstance(self.fw.get_probe_results(results_as="dict"),
                              dict)
        pr1.get_details.assert_called_with(True)
        pr2.get_details.assert_called_with(True)

    def test_fetch_probe_results(self):
        m_pr = MagicMock()
        probename = "probe1"
        m_pr.name = probename
        self.fw.probe_results = [m_pr]
        res = self.fw.fetch_probe_result(probename)
        self.assertEqual(res, m_pr)

    def test_fetch_probe_results_none(self):
        m_pr = MagicMock()
        probename = "probe1"
        m_pr.name = probename
        self.fw.probe_results = []
        with self.assertRaises(IrmaDatabaseError):
            self.fw.fetch_probe_result(probename)

    def test_fetch_probe_results_multiple_results(self):
        m_pr = MagicMock()
        probename = "probe1"
        m_pr.name = probename
        self.fw.probe_results = [m_pr, m_pr]
        with self.assertRaises(IrmaDatabaseError):
            self.fw.fetch_probe_result(probename)

    def test_from_fobj(self):
        filename = "file"
        m_file = MagicMock()
        fw = FileExt(m_file, filename)
        self.assertIs(type(fw), FileExt)
        self.assertEqual(fw.name, "file")

    def test_set_result(self):
        m_pr = MagicMock()
        m_pr.name = "probename"
        self.fw.probe_results = [m_pr]
        probe = "probename"
        result = {'status': 1, 'type': "something"}
        self.fw.file = MagicMock()
        self.fw.set_result(probe, result)

    def test_probes_empty(self):
        self.fw.probe_results = []
        self.assertEqual(self.fw.probes, [])

    def test_probes_not_empty(self):
        m_pr1, m_pr2 = MagicMock(), MagicMock()
        probename1, probename2 = "probename1", "probename2"
        m_pr1.name = probename1
        m_pr2.name = probename2
        self.fw.probe_results = [m_pr1, m_pr2]
        self.assertCountEqual(self.fw.probes, ["probename1", "probename2"])
