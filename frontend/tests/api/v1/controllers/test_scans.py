from random import randint
from unittest import TestCase
from mock import MagicMock, patch
from bottle import HTTPError

import frontend.api.v1.controllers.scans as api_scans
from frontend.models.sqlobjects import Scan, FileWeb
from frontend.api.v1.schemas import ScanSchema_v1
from lib.irma.common.utils import IrmaScanStatus
from bottle import FormsDict


class TestApiScans(TestCase):

    def setUp(self):
        self.old_request = api_scans.request
        self.request = MagicMock()
        self.request.query = FormsDict()
        api_scans.request = self.request

    def tearDown(self):
        api_scans.request = self.old_request
        del self.request

    def test001_initiation(self):
        self.assertIsInstance(api_scans.scan_schema, ScanSchema_v1)

    @patch("frontend.api.v1.controllers.scans.process_error")
    def test002_list_error(self, m_process_error):
        exception = Exception("test")
        db_mock = MagicMock()
        db_mock.query.side_effect = exception
        api_scans.list(db_mock)
        db_mock.query.assert_called_once_with(Scan)
        m_process_error.assert_called_once_with(exception)

    @patch("frontend.api.v1.controllers.scans.scan_schema")
    def test003_list_default(self, m_scan_schema):
        db_mock = MagicMock()
        default_offset, default_limit = 0, 5
        expected = {"total": len(db_mock.query().limit().offset().all()),
                    "offset": default_offset,
                    "limit": default_limit,
                    "data": m_scan_schema.dump().data}
        result = api_scans.list(db_mock)
        self.assertEqual(result, expected)
        self.assertEqual(api_scans.response.content_type,
                         "application/json; charset=UTF-8")
        db_mock.query.assert_called_with(Scan)
        db_mock.query().options().limit.assert_called_with(default_limit)
        m_offset = db_mock.query().options().limit().offset
        m_offset.assert_called_with(default_offset)
        db_mock.query().options().count.assert_not_called()

    @patch("frontend.api.v1.controllers.scans.scan_schema")
    def test004_list_custom_request(self, m_scan_schema):
        db_mock = MagicMock()
        offset, limit = randint(1, 100), randint(1, 100)
        expected = {"total": db_mock.query().options().count(),
                    "offset": offset,
                    "limit": limit,
                    "data": m_scan_schema.dump().data}
        self.request.query['offset'] = offset
        self.request.query['limit'] = limit
        result = api_scans.list(db_mock)
        self.assertEqual(result, expected)
        db_mock.query().options().count.assert_called()

    @patch("frontend.api.v1.controllers.scans.Scan")
    @patch("frontend.api.v1.controllers.scans.scan_schema")
    def test005_new_ok(self, m_scan_schema, m_Scan):
        db_mock = MagicMock()
        expected = m_scan_schema.dumps().data
        result = api_scans.new(db_mock)
        m_Scan.assert_called()
        self.assertIsInstance(m_Scan.call_args[0][0], float)
        self.assertEqual(m_Scan.call_args[0][1], api_scans.request.remote_addr)
        m_Scan().set_status.assert_called_with(IrmaScanStatus.empty)
        self.assertEqual(result, expected)

    @patch("frontend.api.v1.controllers.scans.Scan")
    @patch("frontend.api.v1.controllers.scans.process_error")
    def test006_new_error(self, m_process_error, m_Scan):
        db_mock = MagicMock()
        exception = Exception("test")
        m_Scan.side_effect = exception
        api_scans.new(db_mock)
        self.assertEqual(api_scans.response.content_type,
                         "application/json; charset=UTF-8")
        m_process_error.assert_called_once_with(exception)

    @patch("frontend.api.v1.controllers.scans.Scan")
    @patch("frontend.api.v1.controllers.scans.scan_schema")
    @patch("frontend.api.v1.controllers.scans.validate_id")
    def test007_get_ok(self, m_validate_id, m_scan_schema, m_Scan):
        db_mock = MagicMock()
        expected = m_scan_schema.dumps().data
        scanid = "whatever"
        result = api_scans.get(scanid, db_mock)
        m_validate_id.assert_called_once_with(scanid)
        m_Scan.load_from_ext_id.assert_called_once_with(scanid, db_mock)
        self.assertEqual(result, expected)
        self.assertEqual(api_scans.response.content_type,
                         "application/json; charset=UTF-8")

    @patch("frontend.api.v1.controllers.scans.Scan")
    @patch("frontend.api.v1.controllers.scans.process_error")
    @patch("frontend.api.v1.controllers.scans.validate_id")
    def test008_get_error(self, m_validate_id, m_process_error, m_Scan):
        db_mock = MagicMock()
        exception = Exception("test")
        m_Scan.load_from_ext_id.side_effect = exception
        scanid = "whatever"
        api_scans.get(scanid, db_mock)
        m_process_error.assert_called_once_with(exception)

    @patch("frontend.api.v1.controllers.scans.celery_frontend")
    @patch("frontend.api.v1.controllers.scans.request")
    @patch("frontend.api.v1.controllers.scans.scan_ctrl")
    @patch("frontend.api.v1.controllers.scans.Scan")
    @patch("frontend.api.v1.controllers.scans.scan_schema")
    @patch("frontend.api.v1.controllers.scans.validate_id")
    def test009_launch_ok(self, m_validate_id, m_scan_schema, m_Scan,
                          m_scan_ctrl, m_request, m_celery_frontend):
        db_mock = MagicMock()
        expected = m_scan_schema.dumps().data
        scanid = "whatever"
        probes = ["probe1", "probe2"]
        m_request.json = {'force': True, 'probes': ",".join(probes)}
        result = api_scans.launch(scanid, db_mock)
        m_validate_id.assert_called_once_with(scanid)
        m_Scan.load_from_ext_id.assert_called_once_with(scanid, db_mock)
        m_scan_ctrl.check_probe.assert_called_once_with(
            m_Scan.load_from_ext_id(), probes, db_mock)
        m_celery_frontend.scan_launch.assert_called_once_with(scanid)
        self.assertEqual(result, expected)
        self.assertEqual(api_scans.response.content_type,
                         "application/json; charset=UTF-8")

    @patch("frontend.api.v1.controllers.scans.Scan")
    @patch("frontend.api.v1.controllers.scans.process_error")
    @patch("frontend.api.v1.controllers.scans.validate_id")
    def test010_launch_error(self, m_validate_id, m_process_error, m_Scan):
        db_mock = MagicMock()
        exception = Exception("test")
        m_Scan.load_from_ext_id.side_effect = exception
        scanid = "whatever"
        api_scans.launch(scanid, db_mock)
        m_process_error.assert_called_once_with(exception)

    @patch("frontend.api.v1.controllers.scans.scan_ctrl")
    @patch("frontend.api.v1.controllers.scans.Scan")
    @patch("frontend.api.v1.controllers.scans.scan_schema")
    @patch("frontend.api.v1.controllers.scans.validate_id")
    def test011_cancel_ok(self, m_validate_id, m_scan_schema,
                          m_Scan, m_scan_ctrl):
        db_mock = MagicMock()
        expected = m_scan_schema.dumps().data
        scanid = "whatever"
        result = api_scans.cancel(scanid, db_mock)
        m_validate_id.assert_called_once_with(scanid)
        m_Scan.load_from_ext_id.assert_called_once_with(scanid, db_mock)
        self.assertEqual(result, expected)
        self.assertEqual(api_scans.response.content_type,
                         "application/json; charset=UTF-8")
        m_scan_ctrl.cancel.assert_called_once()

    @patch("frontend.api.v1.controllers.scans.process_error")
    @patch("frontend.api.v1.controllers.scans.validate_id")
    def test012_cancel_error(self, m_validate_id, m_process_error):
        db_mock = MagicMock()
        exception = Exception("test")
        m_validate_id.side_effect = exception
        scanid = "whatever"
        api_scans.cancel(scanid, db_mock)
        m_process_error.assert_called_once_with(exception)

    @patch("frontend.api.v1.controllers.scans.request")
    @patch("frontend.api.v1.controllers.scans.scan_ctrl")
    @patch("frontend.api.v1.controllers.scans.Scan")
    @patch("frontend.api.v1.controllers.scans.scan_schema")
    @patch("frontend.api.v1.controllers.scans.validate_id")
    def test013_add_files_ok(self, m_validate_id, m_scan_schema,
                             m_Scan, m_scan_ctrl, m_request):
        db_mock = MagicMock()
        m_file = MagicMock()
        expected = m_scan_schema.dumps().data
        scanid = "whatever"
        m_file.raw_filename = "filename"
        m_request.files = {'file': m_file}
        result = api_scans.add_files(scanid, db_mock)
        m_validate_id.assert_called_once_with(scanid)
        m_Scan.load_from_ext_id.assert_called_once_with(scanid, db_mock)
        self.assertEqual(result, expected)
        self.assertEqual(api_scans.response.content_type,
                         "application/json; charset=UTF-8")
        m_scan_ctrl.add_files.assert_called_once()

    @patch("frontend.api.v1.controllers.scans.process_error")
    @patch("frontend.api.v1.controllers.scans.validate_id")
    def test014_add_files_error(self, m_validate_id, m_process_error):
        db_mock = MagicMock()
        exception = Exception("test")
        m_validate_id.side_effect = exception
        scanid = "whatever"
        api_scans.add_files(scanid, db_mock)
        m_process_error.assert_called_once_with(exception)

    @patch("frontend.api.v1.controllers.scans.request")
    @patch("frontend.api.v1.controllers.scans.scan_ctrl")
    @patch("frontend.api.v1.controllers.scans.Scan")
    @patch("frontend.api.v1.controllers.scans.scan_schema")
    @patch("frontend.api.v1.controllers.scans.validate_id")
    def test015_add_files_no_files(self, m_validate_id, m_scan_schema,
                                   m_Scan, m_scan_ctrl, m_request):
        db_mock = MagicMock()
        expected = "No files uploaded"
        scanid = "whatever"
        m_request.files = {}
        with self.assertRaises(HTTPError) as context:
            api_scans.add_files(scanid, db_mock)
        m_validate_id.assert_called_once_with(scanid)
        m_Scan.load_from_ext_id.assert_called_once_with(scanid, db_mock)
        self.assertEqual(context.exception.body.message, expected)
        self.assertEqual(api_scans.response.content_type,
                         "application/json; charset=UTF-8")
        m_scan_ctrl.add_files.assert_not_called()

    @patch("frontend.api.v1.controllers.scans.Scan")
    @patch("frontend.api.v1.controllers.scans.FileWebSchema_v1")
    @patch("frontend.api.v1.controllers.scans.validate_id")
    def test015_get_results_ok(self, m_validate_id, m_fw_schema, m_Scan):
        db_mock = MagicMock()
        expected = m_fw_schema().dumps().data
        scanid = "whatever"
        result = api_scans.get_results(scanid, db_mock)
        m_validate_id.assert_called_once_with(scanid)
        m_Scan.load_from_ext_id.assert_called_once_with(scanid, db_mock)
        self.assertEqual(result, expected)
        self.assertEqual(api_scans.response.content_type,
                         "application/json; charset=UTF-8")

    @patch("frontend.api.v1.controllers.scans.process_error")
    @patch("frontend.api.v1.controllers.scans.validate_id")
    def test016_get_results_error(self, m_validate_id, m_process_error):
        db_mock = MagicMock()
        exception = Exception("test")
        m_validate_id.side_effect = exception
        scanid = "whatever"
        api_scans.get_results(scanid, db_mock)
        m_process_error.assert_called_once_with(exception)

    @patch("frontend.api.v1.controllers.scans.FileWeb")
    @patch("frontend.api.v1.controllers.scans.FileWebSchema_v1")
    @patch("frontend.api.v1.controllers.scans.validate_id")
    def test015_get_result_ok(self, m_validate_id, m_fw_schema,
                              m_FileWeb):
        db_mock = MagicMock()
        expected = m_fw_schema().dumps().data
        scanid = "whatever"
        resultid = "whenever"
        result = api_scans.get_result(scanid, resultid, db_mock)
        m_validate_id.assert_called_once_with(resultid)
        m_FileWeb.load_from_ext_id.assert_called_once_with(resultid, db_mock)
        self.assertEqual(result, expected)
        self.assertEqual(api_scans.response.content_type,
                         "application/json; charset=UTF-8")

    @patch("frontend.api.v1.controllers.scans.request")
    @patch("frontend.api.v1.controllers.scans.FileWeb")
    @patch("frontend.api.v1.controllers.scans.validate_id")
    def test016_get_result_formatted_ok(self, m_validate_id, m_FileWeb,
                                        m_request):
        db_mock = MagicMock()
        scanid = "whatever"
        resultid = "whenever"
        m_request.formatted = True
        m_FileWeb.load_from_ext_id.return_value = FileWeb(None, None,
                                                          None, None)
        api_scans.get_result(scanid, resultid, db_mock)
        m_validate_id.assert_called_once_with(resultid)
        m_FileWeb.load_from_ext_id.assert_called_once_with(resultid, db_mock)
        self.assertEqual(api_scans.response.content_type,
                         "application/json; charset=UTF-8")

    @patch("frontend.api.v1.controllers.scans.process_error")
    @patch("frontend.api.v1.controllers.scans.validate_id")
    def test017_get_result_error(self, m_validate_id, m_process_error):
        db_mock = MagicMock()
        exception = Exception("test")
        m_validate_id.side_effect = exception
        scanid = "whatever"
        resultid = "whenever"
        api_scans.get_result(scanid, resultid, db_mock)
        m_process_error.assert_called_once_with(exception)
