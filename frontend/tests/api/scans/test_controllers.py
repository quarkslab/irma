import io
from random import randint, choice
from unittest import TestCase

import api.scans.controllers as api_scans
from api.common.errors import HTTPInvalidParam
from mock import MagicMock, patch

from api.scans.models import Scan, ScanEvents
from api.scans.schemas import ScanSchema
from api.files_ext.schemas import FileExtSchema
from irma.common.base.utils import IrmaScanStatus


class TestScansRoutes(TestCase):
    def assertIsScan(self, data):
        self.assertTrue(type(data) == dict)
        self.assertCountEqual(data.keys(), ScanSchema().fields)

    def assertIsScanList(self, data):
        self.assertTrue(type(data) == list)
        for scan in data:
            self.assertIsScan(scan)

    def assertIsFileExt(self, data):
        self.assertTrue(type(data) == dict)
        self.assertCountEqual(data.keys(), FileExtSchema().fields)

    def assertIsFileWebList(self, data):
        self.assertTrue(type(data) == list)
        for fw in data:
            self.assertIsFileExt(fw)

    def setUp(self):
        self.db = MagicMock()
        self.session = self.db.session
        self.old_db = api_scans.db
        api_scans.db = self.db

    def tearDown(self):
        api_scans.db = self.old_db
        del self.db

    def test_list_error(self):
        exception = Exception("test")
        self.session.query.side_effect = exception
        with self.assertRaises(Exception):
            api_scans.list()
        self.session.query.assert_called_once_with(Scan)

    def test_list_default(self):
        default_offset, default_limit = 0, 5
        result = api_scans.list()
        self.assertEqual(result["offset"], default_offset)
        self.assertEqual(result["limit"], default_limit)
        self.session.query.assert_called_with(Scan)
        self.session.query().limit.assert_called_with(default_limit)
        m_offset = self.session.query().limit().offset
        m_offset.assert_called_with(default_offset)
        self.session.query().count.assert_not_called()

    def test_list_custom_request_no_status(self):
        offset, limit = randint(1, 100), randint(1, 100)
        status = choice(list(IrmaScanStatus.label.values()))
        result = api_scans.list(offset=offset, limit=limit)
        self.assertEqual(result["offset"], offset)
        self.assertEqual(result["limit"], limit)
        self.assertIsScanList(result["data"])
        self.session.query().count.assert_called()

    def test_list_custom_request_status(self):
        offset, limit = randint(1, 100), randint(1, 100)
        status = choice(list(IrmaScanStatus.label.values()))
        for (k, v) in IrmaScanStatus.label.items():
            if v == status:
                status_code = k
                break
        result = api_scans.list(status=status, offset=offset, limit=limit)
        self.assertEqual(result["offset"], offset)
        self.assertEqual(result["limit"], limit)
        self.assertIsScanList(result["data"])
        self.session.query().filter().count.assert_called()

    def test_list_custom_request_status_not_existing(self):
        offset, limit = randint(1, 100), randint(1, 100)
        with self.assertRaises(api_scans.HTTPInvalidParam):
            api_scans.list(status="whatever", offset=offset, limit=limit)

    @patch("api.scans.controllers.Scan")
    def test_new_ok(self, m_Scan):
        m_request = MagicMock()
        result = api_scans.new(m_request)
        m_Scan.assert_called()
        self.assertIsInstance(m_Scan.call_args[0][0], float)
        self.assertEqual(m_Scan.call_args[0][1], m_request.remote_addr)
        m_Scan().set_status.assert_called_with(IrmaScanStatus.empty)
        self.assertIsScan(result)

    @patch("api.scans.controllers.Scan")
    def test_new_error(self, m_Scan):
        exception = Exception("test")
        m_Scan.side_effect = exception
        m_request = MagicMock()
        with self.assertRaises(Exception):
            api_scans.new(m_request)

    @patch("api.scans.controllers.Scan")
    def test_get_ok(self, m_Scan):
        m_scan = MagicMock()
        m_Scan.load_from_ext_id.return_value = m_scan
        scan_id = "whatever"
        result = api_scans.get(scan_id)
        m_Scan.load_from_ext_id.assert_called_once_with(scan_id, self.session)
        self.assertIsScan(result)

    @patch("api.scans.controllers.Scan")
    def test_get_error(self, m_Scan):
        exception = Exception("test")
        m_Scan.load_from_ext_id.side_effect = exception
        scan_id = "whatever"
        with self.assertRaises(Exception):
            api_scans.get(scan_id)

    @patch("api.scans.controllers.celery_frontend")
    @patch("api.probes.services.check_probe")
    @patch("api.scans.controllers.Scan")
    def test_launch_v1_ok(self, m_Scan, m_check_probe, m_celery_frontend):
        scan_id = "whatever"
        probes = ["probe1", "probe2"]
        force = "False"
        mimetype_filtering = "False"
        resubmit_files = "False"
        m_check_probe.return_value = []

        m_scan = Scan("date", "ip")
        m_check_probe.assert_called_once_with(None)

        m_scan.force = None
        m_scan.mimetype_filtering = None
        m_scan.resubmit_files = None
        m_scan.events = [ScanEvents(IrmaScanStatus.empty, m_scan)]
        m_Scan.load_from_ext_id.return_value = m_scan
        result = api_scans.launch_v1(scan_id=scan_id,
                                     probes=probes,
                                     force=force,
                                     mimetype_filtering=mimetype_filtering,
                                     resubmit_files=resubmit_files
                                     )
        m_check_probe.assert_called()
        m_Scan.load_from_ext_id.assert_called_once_with(scan_id, self.session)
        m_celery_frontend.scan_launch.assert_called_once_with(scan_id)
        self.assertIsScan(result)
        self.assertEqual(result["force"], force, "force")
        self.assertEqual(result["mimetype_filtering"], mimetype_filtering,
                         "mimetype")
        self.assertEqual(result["resubmit_files"], resubmit_files, "resubmit")

    @patch("api.scans.controllers.Scan")
    def test_launch_v1_error(self, m_Scan):
        exception = Exception("test")
        m_Scan.load_from_ext_id.side_effect = exception
        scan_id = "whatever"
        probes = ["probe1", "probe2"]
        force = False
        mimetype_filtering = False
        resubmit_files = False
        with self.assertRaises(Exception):
            api_scans.launch_v1(scan_id=scan_id,
                                probes=probes,
                                force=force,
                                mimetype_filtering=mimetype_filtering,
                                resubmit_files=resubmit_files
                                )

    @patch("api.scans.controllers.FileExt")
    @patch("api.scans.controllers.celery_frontend")
    @patch("api.scans.controllers.probe_ctrl.check_probe")
    def test_launch_v2_ok(self, m_check_probe, m_celery_frontend, m_FileExt):
        m_request = MagicMock()
        force = False
        mimetype_filtering = False
        resubmit_files = False
        probes = ["probe1", "probe2"]
        m_body = {
            "files": ["file_ext1"],
            "options": {
                "probes": probes,
                "force": force,
                "mimetype_filtering": mimetype_filtering,
                "resubmit_files": resubmit_files,
            }
        }
        m_file_ext = MagicMock()
        m_file_ext.scan = None
        m_FileExt.load_from_ext_id.return_value = m_file_ext
        result = api_scans.launch_v2(m_request, m_body)
        m_check_probe.assert_called_once_with(probes)
        m_celery_frontend.scan_launch.assert_called_once()
        self.assertIsScan(result)
        self.assertEqual(result["force"], str(force),
                         "force value is wrong")
        self.assertEqual(result["mimetype_filtering"], str(mimetype_filtering),
                         "mimetype_filtering value is wrong")
        self.assertEqual(result["resubmit_files"], str(resubmit_files),
                         "resubmit_files value is wrong")

    @patch("api.scans.controllers.FileExt")
    @patch("api.scans.controllers.celery_frontend")
    @patch("api.scans.controllers.probe_ctrl")
    def test_launch_v2_file_deleted(self, m_probe_ctrl, m_celery_frontend,
                                    m_FileExt):
        m_request = MagicMock()
        force = False
        mimetype_filtering = False
        resubmit_files = False
        probes = ["probe1", "probe2"]
        m_body = {
            "files": ["file_ext1"],
            "options": {
                "probes": probes,
                "force": force,
                "mimetype_filtering": mimetype_filtering,
                "resubmit_files": resubmit_files,
            }
        }
        sha256 = "whatever"
        m_file_ext, m_file = MagicMock(), MagicMock()
        m_file.path = None
        m_file_ext.file = m_file
        m_file_ext.file.sha256 = sha256
        m_file_ext.scan = None
        m_FileExt.load_from_ext_id.return_value = m_file_ext
        expected = "The \"files\" parameter is invalid. File with hash " \
                   "%s should be (re)uploaded" % sha256
        with self.assertRaises(api_scans.HTTPInvalidParam) as context:
            api_scans.launch_v2(m_request, m_body)
        m_probe_ctrl.check_probe.assert_not_called()
        m_celery_frontend.scan_launch.assert_not_called()
        self.assertEqual(context.exception.description, expected)

    @patch("api.scans.controllers.FileExt")
    @patch("api.scans.controllers.celery_frontend")
    @patch("api.scans.controllers.probe_ctrl")
    def test_launch_v2_file_not_found(self, m_probe_ctrl, m_celery_frontend,
                                      m_FileExt):
        m_request = MagicMock()
        force = False
        mimetype_filtering = False
        resubmit_files = False
        probes = ["probe1", "probe2"]
        m_body = {
            "files": ["file_ext1", "file_ext2"],
            "options": {
                "probes": probes,
                "force": force,
                "mimetype_filtering": mimetype_filtering,
                "resubmit_files": resubmit_files,
            }
        }
        m_FileExt.load_from_ext_id.side_effect = \
            api_scans.IrmaDatabaseResultNotFound
        expected = "The \"files\" parameter is invalid. File file_ext1 " \
                   "not found"
        with self.assertRaises(api_scans.HTTPInvalidParam) as context:
            api_scans.launch_v2(m_request, m_body)
        m_probe_ctrl.check_probe.assert_not_called()
        m_celery_frontend.scan_launch.assert_not_called()
        self.assertEqual(context.exception.description, expected)

    @patch("api.scans.controllers.FileWeb")
    @patch("api.scans.controllers.celery_frontend")
    @patch("api.scans.controllers.probe_ctrl")
    def test_launch_v2_file_already_scanned(self, m_probe_ctrl,
                                            m_celery_frontend, m_FileWeb):
        m_request = MagicMock()
        force = False
        mimetype_filtering = False
        resubmit_files = False
        probes = ["probe1", "probe2"]
        m_body = {
            "files": ["fileweb1"],
            "options": {
                "probes": probes,
                "force": force,
                "mimetype_filtering": mimetype_filtering,
                "resubmit_files": resubmit_files,
            }
        }
        m_file_ext = MagicMock()
        m_file_ext.scan = "scanid1"
        m_FileWeb.load_from_ext_id.return_value = m_file_ext
        expected = "The \"files\" parameter is invalid. File fileweb1 " \
                   "already scanned"
        with self.assertRaises(api_scans.HTTPInvalidParam) as context:
            api_scans.launch_v2(m_request, m_body)
        m_probe_ctrl.check_probe.assert_not_called()
        m_celery_frontend.scan_launch.assert_not_called()
        self.assertEqual(context.exception.description, expected)

    def test_launch_v2_error(self):
        m_body = MagicMock()
        m_request = MagicMock()
        with self.assertRaises(HTTPInvalidParam):
            api_scans.launch_v2(m_request, m_body)

    def test_launch_v2_no_body(self):
        m_body = None
        m_request = MagicMock()
        with self.assertRaises(HTTPInvalidParam):
            api_scans.launch_v2(m_request, m_body)

    def test_launch_v2_force_wrong_type(self):
        m_request = MagicMock()
        m_body = {"files": [MagicMock()],
                  "options": {"force": 15,
                              "mimetype_filtering": True,
                              "resubmit_files": True}}
        with self.assertRaises(HTTPInvalidParam):
            api_scans.launch_v2(m_request, m_body)

    def test_launch_v2_mimetype_filtering_wrong_type(self):
        m_request = MagicMock()
        m_body = {"files": [MagicMock()],
                  "options": {"force": True,
                              "mimetype_filtering": 42,
                              "resubmit_files": True}}
        with self.assertRaises(HTTPInvalidParam):
            api_scans.launch_v2(m_request, m_body)

    def test_launch_v2_resubmit_files_wrong_type(self):
        m_request = MagicMock()
        m_body = {"files": [MagicMock()],
                  "options": {"force": True,
                              "mimetype_filtering": True,
                              "resubmit_files": 17}}
        with self.assertRaises(HTTPInvalidParam):
            api_scans.launch_v2(m_request, m_body)

    @patch("api.scans.controllers.scan_ctrl")
    @patch("api.scans.controllers.Scan")
    def test_cancel_ok(self, m_Scan, m_scan_ctrl):
        scan_id = "whatever"
        result = api_scans.cancel(scan_id)
        m_Scan.load_from_ext_id.assert_called_once_with(scan_id, self.session)
        self.assertIsScan(result)
        m_scan_ctrl.cancel.assert_called_once()

    @patch("api.scans.controllers.Scan")
    def test_cancel_raises(self, m_Scan):
        scan_id = "whatever"
        m_Scan.load_from_ext_id.side_effect = Exception()
        with self.assertRaises(Exception):
            api_scans.cancel(scan_id)

    @patch("api.scans.controllers.File")
    @patch("api.scans.controllers.FileExt")
    @patch("api.scans.controllers.IrmaScanStatus")
    @patch("api.scans.controllers.Scan")
    def test_add_files_ok(self, m_Scan, m_IrmaScanStatus, m_FileExt, m_File):
        m_file = MagicMock()
        m_request = MagicMock()
        scan_id = "whatever"
        data = b"DATA"
        filename = "filename"
        m_file.filename = filename
        m_file.file = io.BytesIO(data)
        m_request._params = {'files': m_file}
        result = api_scans.add_files(m_request, scan_id)
        m_Scan.load_from_ext_id.assert_called_once_with(scan_id, self.session)
        self.assertIsScan(result)

    @patch("api.scans.controllers.IrmaScanStatus")
    @patch("api.scans.controllers.scan_ctrl")
    @patch("api.scans.controllers.Scan")
    def test_add_files_no_files(self, m_Scan, m_scan_ctrl, m_IrmaScanStatus):
        scan_id = "whatever"
        m_request = MagicMock()
        m_request.files = {}
        expected = "The \"files\" parameter is invalid. Empty list"
        with self.assertRaises(HTTPInvalidParam) as context:
            api_scans.add_files(m_request, scan_id=scan_id)
        m_Scan.load_from_ext_id.assert_called_once_with(scan_id, self.session)
        self.assertEqual(context.exception.description, expected)
        m_scan_ctrl.add_files.assert_not_called()

    @patch("api.scans.controllers.Scan")
    def test_get_results_ok(self, m_Scan):
        scan_id = "whatever"
        result = api_scans.get_results(scan_id)
        m_Scan.load_from_ext_id.assert_called_once_with(scan_id, self.session)
        self.assertIsFileWebList(result)

    @patch("api.scans.controllers.Scan")
    def test_get_results_raises(self, m_Scan):
        scan_id = "whatever"
        m_Scan.load_from_ext_id.side_effect = Exception()
        with self.assertRaises(Exception):
            api_scans.get_results(scan_id)

    @patch("api.scans.controllers.Scan")
    def test_get_report(self, m_Scan):
        request = MagicMock()
        response = MagicMock()

        m_scan = MagicMock()
        m_scan.external_id = "whatever"
        m_scan.finished.return_value = True

        def side_effect(scan_id, session):
            if scan_id == m_scan.external_id:
                return m_scan

        m_Scan.load_from_ext_id.side_effect = side_effect

        self.assertEqual(api_scans.get_report(request, response,
                                              m_scan.external_id),
                         m_scan)

    @patch("api.scans.controllers.Scan")
    def test_get_report_error(self, m_Scan):
        request = MagicMock()
        response = MagicMock()

        m_scan = MagicMock()
        m_scan.external_id = "whatever"
        m_scan.finished.return_value = False

        def side_effect(scan_id, session):
            if scan_id == m_scan.external_id:
                return m_scan

        m_Scan.load_from_ext_id.side_effect = side_effect

        with self.assertRaises(api_scans.HTTPUnauthorized):
            api_scans.get_report(request, response, m_scan.external_id)

    @patch("api.scans.controllers.Scan")
    @patch("api.scans.controllers.FileExt")
    @patch("api.scans.controllers.celery_frontend")
    @patch("api.scans.controllers.files_ctrl")
    def test_quick_scan(self, m_files_ctrl, m_celery_frontend, m_FileExt,
                        m_Scan):
        m_request = MagicMock()
        m_file_ext = MagicMock()
        m_FileExt.load_from_ext_id.return_value = m_file_ext
        m_Scan.return_value.external_id = "extid_HOvDI2"

        result = api_scans.quick_scan(m_request)

        m_files_ctrl.create.assert_called_once_with(m_request)
        m_celery_frontend.scan_launch.assert_called_once_with("extid_HOvDI2")
        self.assertIsScan(result)
