from unittest import TestCase
from mock import MagicMock, PropertyMock, patch

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from brain.models.sqlobjects import Scan
from irma.common.base.utils import IrmaScanStatus
from irma.common.base.exceptions import IrmaDatabaseError, \
    IrmaDatabaseResultNotFound


class TestModelsScan(TestCase):
    def setUp(self):
        self.frontend_scanid = "frontend_scanid"
        self.user_id = "user_id"
        self.session = MagicMock()

    def test___init__(self):
        scan = Scan(self.frontend_scanid, self.user_id)
        self.assertEqual(scan.scan_id, self.frontend_scanid)
        self.assertEqual(scan.user_id, self.user_id)
        self.assertEqual(scan.status, IrmaScanStatus.empty)
        self.assertIsNotNone(scan.timestamp)

    def test_nb_files(self):
        with patch('brain.models.sqlobjects.Scan.files',
                   new_callable=PropertyMock) as mock_files:
            mock_files.return_value = {}
            scan = Scan(self.frontend_scanid, self.user_id)
            self.assertEqual(scan.nb_files, 0)
            mock_files.assert_called_once()

    def test_get_scan(self):
        scan_id = "scan_id"
        Scan.get_scan(scan_id, self.user_id, self.session)
        self.session.query.assert_called_once_with(Scan)
        m_filter = self.session.query(Scan).filter
        m_filter.assert_called_once()
        m_filter().one.assert_called_once()

    def test_get_scan_not_found(self):
        self.session.query.side_effect = NoResultFound
        with self.assertRaises(IrmaDatabaseResultNotFound):
            Scan.get_scan("whatever", self.user_id, self.session)

    def test_get_scan_multiple_found(self):
        self.session.query.side_effect = MultipleResultsFound
        with self.assertRaises(IrmaDatabaseError):
            Scan.get_scan("whatever", self.user_id, self.session)
