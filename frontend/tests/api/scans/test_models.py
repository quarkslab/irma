from unittest import TestCase
from random import choice, randint
from mock import MagicMock, patch

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from api.scans.models import Scan
from irma.common.base.utils import IrmaScanStatus
from irma.common.base.exceptions import IrmaCoreError, \
    IrmaDatabaseResultNotFound, IrmaDatabaseError


class TestScan(TestCase):

    @patch("api.probes.services.check_probe")
    def setUp(self, m_check_probe):
        m_check_probe.return_value = []
        self.date = "date"
        self.ip = "ip"
        self.scan = Scan(self.date, self.ip)

    def tearDown(self):
        del self.scan

    def test_finished_not_uploaded(self):
        status = choice([IrmaScanStatus.empty,
                         IrmaScanStatus.ready])
        self.scan.set_status(status)
        self.assertFalse(self.scan.finished())

    def test_finished_launched_not_finished(self):
        file_ext = MagicMock()
        file_ext.status = None
        self.scan.files_ext = [file_ext]
        self.scan.set_status(IrmaScanStatus.launched)
        self.assertFalse(self.scan.finished())

    def test_finished_launched_finished(self):
        a, b = MagicMock(), MagicMock()
        a.doc = "something"
        b.doc = "anotherthing"
        fw = MagicMock()
        fw.probe_results = [a, b]
        self.scan.files_web = [fw]
        self.scan.set_status(IrmaScanStatus.launched)
        self.assertTrue(self.scan.finished())

    def test_finished_finished(self):
        self.scan.set_status(IrmaScanStatus.launched)
        res = self.scan.finished()
        self.assertTrue(res)

    def test_probes_total(self):
        file_ext1, file_ext2 = MagicMock(), MagicMock()
        pt1, pt2 = randint(0, 20), randint(0, 20)
        file_ext1.probes_total = pt1
        file_ext2.probes_total = pt2
        self.scan.files_ext = [file_ext1, file_ext2]
        self.assertEqual(self.scan.probes_total, pt1 + pt2)

    def test_probes_finished(self):
        file_ext1, file_ext2 = MagicMock(), MagicMock()
        pf1, pf2 = randint(0, 20), randint(0, 20)
        file_ext1.probes_finished = pf1
        file_ext2.probes_finished = pf2
        self.scan.files_ext = [file_ext1, file_ext2]
        self.assertEqual(self.scan.probes_finished, pf1 + pf2)

    def test_files(self):
        file_ext = MagicMock()
        self.scan.files_ext = [file_ext]
        self.assertEqual(self.scan.files, [file_ext.file])

    def test_set_status(self):
        with self.assertRaises(IrmaCoreError):
            self.scan.set_status("whatever")

    def test_load_from_ext_id(self):
        m_session = MagicMock()
        m_query = MagicMock()
        m_session.query.return_value = m_query
        external_id = "whatever"
        Scan.load_from_ext_id(external_id, m_session)
        m_filter = m_query.options().filter
        m_filter.assert_called_once()

    def test_load_from_ext_id_none(self):
        m_session = MagicMock()
        external_id = "whatever"
        m_filter = m_session.query().options().filter
        m_filter.side_effect = NoResultFound()
        with self.assertRaises(IrmaDatabaseResultNotFound):
            Scan.load_from_ext_id(external_id, m_session)

    def test_load_from_ext_id_multiple(self):
        m_session = MagicMock()
        external_id = "whatever"
        m_filter = m_session.query().options().filter
        m_filter.side_effect = MultipleResultsFound()
        with self.assertRaises(IrmaDatabaseError):
            Scan.load_from_ext_id(external_id, m_session)

    def test_set_get_probelist(self):
        probelist = ["probe1", "probe2"]
        self.scan.set_probelist(probelist)
        self.assertCountEqual(self.scan.get_probelist(), probelist)

    def test_finished(self):
        self.scan.set_status(IrmaScanStatus.finished)
        self.assertTrue(self.scan.finished())
