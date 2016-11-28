from unittest import TestCase
from random import choice, randint
from mock import MagicMock

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from frontend.models.sqlobjects import File, Scan
from lib.irma.common.utils import IrmaScanStatus
from lib.irma.common.exceptions import IrmaCoreError, \
    IrmaDatabaseResultNotFound, IrmaDatabaseError


class TestScan(TestCase):

    def setUp(self):
        self.date = "date"
        self.ip = "ip"
        self.scan = Scan(self.date, self.ip)

    def tearDown(self):
        del self.scan

    def test001_finished_not_uploaded(self):
        status = choice([IrmaScanStatus.empty,
                         IrmaScanStatus.ready])
        self.scan.set_status(status)
        self.assertFalse(self.scan.finished())

    def test002_finished_launched_not_finished(self):
        a, b = MagicMock(), MagicMock()
        a.doc = "something"
        b.doc = None
        fw = MagicMock()
        fw.probe_results = [a, b]
        self.scan.files_web = [fw]
        self.scan.set_status(IrmaScanStatus.launched)
        self.assertFalse(self.scan.finished())

    def test003_finished_launched_finished(self):
        a, b = MagicMock(), MagicMock()
        a.doc = "something"
        b.doc = "anotherthing"
        fw = MagicMock()
        fw.probe_results = [a, b]
        self.scan.files_web = [fw]
        self.scan.set_status(IrmaScanStatus.launched)
        self.assertTrue(self.scan.finished())

    def test004_finished_finished(self):
        self.scan.set_status(IrmaScanStatus.launched)
        res = self.scan.finished()
        self.assertTrue(res)

    def test005_probes_total(self):
        fw1, fw2 = MagicMock(), MagicMock()
        pt1, pt2 = randint(0, 20), randint(0, 20)
        fw1.probes_total = pt1
        fw2.probes_total = pt2
        self.scan.files_web = [fw1, fw2]
        self.assertEquals(self.scan.probes_total, pt1 + pt2)

    def test006_probes_finished(self):
        fw1, fw2 = MagicMock(), MagicMock()
        pf1, pf2 = randint(0, 20), randint(0, 20)
        fw1.probes_finished = pf1
        fw2.probes_finished = pf2
        self.scan.files_web = [fw1, fw2]
        self.assertEquals(self.scan.probes_finished, pf1 + pf2)

    def test007_files(self):
        fw = MagicMock()
        self.scan.files_web = [fw]
        self.assertEqual(self.scan.files, [fw.file])

    def test008_set_status(self):
        with self.assertRaises(IrmaCoreError):
            self.scan.set_status("whatever")

    def test009_fileweb_by_sha256(self):
        fw = MagicMock()
        sha256 = "whatever"
        fw.file.sha256 = sha256
        self.scan.files_web = [fw]
        self.assertEqual(self.scan.get_filewebs_by_sha256(sha256), [fw])

    def test010_query_find_by_filesha256(self):
        m_session = MagicMock()
        sha256 = "whatever"
        Scan.query_find_by_filesha256(sha256, m_session)
        m_filter = m_session.query(Scan).join().join().filter
        m_filter.is_called_once_with(File.sha256 == sha256)

    def test011_load_from_ext_id(self):
        m_session = MagicMock()
        m_query = MagicMock()
        m_session.query.return_value = m_query
        external_id = "whatever"
        Scan.load_from_ext_id(external_id, m_session)
        m_filter = m_query.options().filter
        m_filter.assert_called_once()

    def test012_load_from_ext_id_none(self):
        m_session = MagicMock()
        external_id = "whatever"
        m_filter = m_session.query().options().filter
        m_filter.side_effect = NoResultFound()
        with self.assertRaises(IrmaDatabaseResultNotFound):
            Scan.load_from_ext_id(external_id, m_session)

    def test013_load_from_ext_id_multiple(self):
        m_session = MagicMock()
        external_id = "whatever"
        m_filter = m_session.query().options().filter
        m_filter.side_effect = MultipleResultsFound()
        with self.assertRaises(IrmaDatabaseError):
            Scan.load_from_ext_id(external_id, m_session)

    def test014_set_get_probelist(self):
        probelist = ["probe1", "probe2"]
        self.scan.set_probelist(probelist)
        self.assertItemsEqual(self.scan.get_probelist(), probelist)

    def test015_finished(self):
        self.scan.set_status(IrmaScanStatus.finished)
        self.assertTrue(self.scan.finished())
