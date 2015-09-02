from random import randint
from unittest import TestCase
from mock import MagicMock, patch

import frontend.api.v1.controllers.scans as api_scans
from frontend.models.sqlobjects import Scan
from frontend.api.v1.schemas import ScanSchema_v1
from lib.irma.common.utils import IrmaScanStatus


class TestApiScans(TestCase):

    def test001_initiation(self):
        self.assertIsInstance(api_scans.scan_schema, ScanSchema_v1)

    def test002_list_error(self):
        sample = Exception("test")
        db_mock = MagicMock()
        db_mock.query.side_effect = sample
        with patch("frontend.api.v1.controllers.scans.process_error") as mock:
            api_scans.list(db_mock)
        self.assertTrue(db_mock.query.called)
        self.assertEqual(db_mock.query.call_args, ((Scan,),))
        self.assertTrue(mock.called)
        self.assertEqual(mock.call_args, ((sample,),))

    def test003_list_default(self):
        db_mock = MagicMock()
        default_offset, default_limit = 0, 5
        scan_schema_mock = MagicMock()
        expected = {"total": len(db_mock.query().limit().offset().all()),
                    "offset": default_offset,
                    "limit": default_limit,
                    "data": scan_schema_mock.dump().data}
        api_scans.request.query.offset = None
        api_scans.request.query.limit = None
        scan_schema = "frontend.api.v1.controllers.scans.scan_schema"
        with patch(scan_schema, scan_schema_mock):
            result = api_scans.list(db_mock)
        self.assertEqual(result, expected)
        self.assertEqual(api_scans.response.content_type,
                         "application/json; charset=UTF-8")
        self.assertEqual(db_mock.query.call_args, ((Scan,),))
        self.assertEqual(db_mock.query().limit.call_args, ((default_limit,),))
        self.assertEqual(db_mock.query().limit().offset.call_args,
                         ((default_offset,),))
        self.assertFalse(db_mock.query().count.called)

    def test004_list_custom_request(self):
        db_mock = MagicMock()
        scan_schema_mock = MagicMock()
        offset, limit = randint(1, 100), randint(1, 100)
        expected = {"total": db_mock.query().count(),
                    "offset": offset,
                    "limit": limit,
                    "data": scan_schema_mock.dump().data}
        api_scans.request.query.offset = offset
        api_scans.request.query.limit = limit
        scan_schema = "frontend.api.v1.controllers.scans.scan_schema"
        with patch(scan_schema, scan_schema_mock):
            result = api_scans.list(db_mock)
        self.assertEqual(result, expected)
        self.assertTrue(db_mock.query().count.called)

    def test005_new_ok(self):
        db_mock = MagicMock()
        with patch("frontend.api.v1.controllers.scans.Scan") as scan_mock:
            scan_schema = "frontend.api.v1.controllers.scans.scan_schema"
            with patch(scan_schema) as schema_mock:
                result = api_scans.new(db_mock)
        self.assertTrue(scan_mock.called)
        self.assertIsInstance(scan_mock.call_args[0][0], float)
        self.assertEqual(scan_mock.call_args[0][1],
                         api_scans.request.remote_addr)
        self.assertTrue(db_mock.add.called)
        self.assertEqual(db_mock.add.call_args, ((scan_mock(),),))
        self.assertTrue(scan_mock().set_status.called)
        self.assertEqual(scan_mock().set_status.call_args,
                         ((IrmaScanStatus.empty,),))
