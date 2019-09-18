from tempfile import TemporaryFile
from unittest import TestCase

from mock import MagicMock, patch

import api.scans.services as module
from irma.common.base.exceptions import IrmaValueError, IrmaTaskError, \
    IrmaFtpError, IrmaDatabaseError
from irma.common.base.utils import IrmaReturnCode
from irma.common.base.utils import IrmaScanStatus


class TestModuleScanctrl(TestCase):

    def setUp(self):
        self.old_Scan = module.Scan
        self.old_celery_brain = module.celery_brain
        self.Scan = MagicMock()

        self.celery_brain = MagicMock()
        module.Scan = self.Scan
        module.celery_brain = self.celery_brain

    def tearDown(self):
        module.Scan = self.old_Scan
        module.celery_brain = self.old_celery_brain
        del self.Scan
        del self.celery_brain

    def test_cancel_status_empty(self):
        scan, session = MagicMock(), MagicMock()
        scan.status = IrmaScanStatus.empty
        res = module.cancel(scan, session)
        self.assertIsNone(res)
        scan.set_status.assert_called_once_with(IrmaScanStatus.cancelled)

    def test_cancel_status_ready(self):
        scan, session = MagicMock(), MagicMock()
        scan.status = IrmaScanStatus.ready
        res = module.cancel(scan, session)
        self.assertIsNone(res)
        scan.set_status.assert_called_once_with(IrmaScanStatus.cancelled)

    def test_cancel_status_uploaded(self):
        scan, session = MagicMock(), MagicMock()
        scan.status = IrmaScanStatus.uploaded
        label = IrmaScanStatus.label[scan.status]
        expected = "can not cancel scan in {} status".format(label)
        with self.assertRaises(IrmaValueError) as context:
            module.cancel(scan, session)
        self.assertEqual(str(context.exception), expected)

    def test_cancel_status_launched_ok(self):
        scan, session = MagicMock(), MagicMock()
        scan.status = IrmaScanStatus.launched
        retcode = IrmaReturnCode.success
        cancel_res = {'cancel_details': "details"}
        self.celery_brain.scan_cancel.return_value = (retcode, cancel_res)
        res = module.cancel(scan, session)
        self.assertEqual(res, cancel_res['cancel_details'])
        scan.set_status.assert_called_once_with(IrmaScanStatus.cancelled)

    def test_cancel_status_launched_status_processed(self):
        scan, session = MagicMock(), MagicMock()
        scan.status = IrmaScanStatus.launched
        retcode = IrmaReturnCode.success
        status = IrmaScanStatus.label[IrmaScanStatus.processed]
        cancel_res = {'status': status}
        self.celery_brain.scan_cancel.return_value = (retcode, cancel_res)
        with self.assertRaises(IrmaValueError) as context:
            module.cancel(scan, session)
        self.assertEqual(str(context.exception),
                         "can not cancel scan in {0} status".format(status))
        scan.set_status.assert_called_once_with(IrmaScanStatus.processed)

    def test_cancel_status_launched_status_error(self):
        scan, session = MagicMock(), MagicMock()
        scan.status = IrmaScanStatus.error_ftp_upload
        res = module.cancel(scan, session)
        self.assertIsNone(res)
        scan.set_status.assert_not_called()

    def test_cancel_status_launched_brain_error(self):
        scan, session = MagicMock(), MagicMock()
        scan.status = IrmaScanStatus.launched
        retcode = IrmaReturnCode.error
        ret_val = "reason"
        self.celery_brain.scan_cancel.return_value = (retcode, ret_val)
        with self.assertRaises(IrmaTaskError) as context:
            module.cancel(scan, session)
        self.assertEqual(str(context.exception),
                         ret_val)
        scan.set_status.assert_not_called()

    def test_cancel_status_processed(self):
        scan, session = MagicMock(), MagicMock()
        scan.status = IrmaScanStatus.processed
        label = IrmaScanStatus.label[scan.status]
        expected = "can not cancel scan in {} status".format(label)
        with self.assertRaises(IrmaValueError) as context:
            module.cancel(scan, session)
        self.assertEqual(str(context.exception), expected)

    def test_cancel_status_flushed(self):
        scan, session = MagicMock(), MagicMock()
        scan.status = IrmaScanStatus.flushed
        label = IrmaScanStatus.label[scan.status]
        expected = "can not cancel scan in {} status".format(label)
        with self.assertRaises(IrmaValueError) as context:
            module.cancel(scan, session)
        self.assertEqual(str(context.exception), expected)

    def test_cancel_status_cancelling(self):
        scan, session = MagicMock(), MagicMock()
        scan.status = IrmaScanStatus.cancelling
        label = IrmaScanStatus.label[scan.status]
        expected = "can not cancel scan in {} status".format(label)
        with self.assertRaises(IrmaValueError) as context:
            module.cancel(scan, session)
        self.assertEqual(str(context.exception), expected)

    def test_cancel_status_cancelled(self):
        scan, session = MagicMock(), MagicMock()
        scan.status = IrmaScanStatus.cancelled
        label = IrmaScanStatus.label[scan.status]
        expected = "can not cancel scan in {} status".format(label)
        with self.assertRaises(IrmaValueError) as context:
            module.cancel(scan, session)
        self.assertEqual(str(context.exception), expected)

    def test_set_status_launched_status_uploaded(self):
        scan = MagicMock()
        scan.status = IrmaScanStatus.uploaded
        self.Scan.load_from_ext_id.return_value = scan
        module.set_status("whatever", IrmaScanStatus.launched)
        scan.set_status.assert_called_with(IrmaScanStatus.launched)

    def test_set_status_launched_not_uploaded(self):
        scan = MagicMock()
        scan.status = IrmaScanStatus.finished
        self.Scan.load_from_ext_id.return_value = scan
        module.set_status("whatever", IrmaScanStatus.launched)
        self.assertEqual(scan.status, IrmaScanStatus.finished)

    @patch("api.scans.services.File")
    @patch("api.scans.services.FileProbeResult")
    @patch("api.scans.services.ftp_ctrl")
    def test_append_new_files(self, m_ftpctrl, m_FileProbeResult, m_File):
        m_scan, m_session = MagicMock(), MagicMock()
        m_scan._sa_instance_state.session = m_session
        filename = "filename"
        fileid = "fileid"
        uploaded_files = {filename: fileid}
        m_fobj = MagicMock()
        m_proberesult = MagicMock()
        m_ftpctrl.download_file_data.return_value = m_fobj
        module._append_new_files_to_scan(m_scan, uploaded_files,
                                         m_proberesult, 1)
        m_download = m_ftpctrl.download_file_data
        m_download.assert_called_once_with(fileid)
        m_File.get_or_create.assert_called_once_with(m_fobj, m_session)
        m_FileProbeResult.assert_called_once_with(m_File.get_or_create(),
                                                  filename,
                                                  m_proberesult, 1)

    def test_sanitize_res(self):
        pattern = "\u0000test" + "\x00"
        pattern_expected = "test"
        dic_key = "te.st$key"
        dic_expected = "te_stkey"
        dic = {'unicode': pattern,
               'list': [pattern],
               'dict': {dic_key: pattern},
               'else': "else"}
        expected = {'unicode': pattern_expected,
                    'list': [pattern_expected],
                    'dict': {dic_expected: pattern_expected},
                    'else': "else"}
        res = module._sanitize_res(dic)
        self.assertCountEqual(res.values(), expected.values())

    def test_add_empty_result_refresult(self):
        fw, scan, session = MagicMock(), MagicMock(), MagicMock()
        pr1, pr2 = MagicMock(), MagicMock()
        probe1, probe2 = "Probe1", "Probe2"
        probelist = [probe1, probe2]
        pr1.name = probe1
        pr2.name = probe2
        scan.force = False
        m_get_ref_result = MagicMock(
                side_effect=lambda x: (pr1 if x == pr1.name else pr2))
        fw.file.get_ref_result = m_get_ref_result
        fw.probe_results = []
        module._add_empty_result(fw, probelist, scan, session)
        self.assertCountEqual(fw.probe_results, [pr1, pr2])

    @patch("api.scans.services.ProbeResult")
    def test_add_empty_result_noresult(self, m_ProbeResult):
        fw, scan, session = MagicMock(), MagicMock(), MagicMock()
        probe1, probe2 = "Probe1", "Probe2"
        probelist = [probe1, probe2]
        scan.force = True
        fw.probe_results = []
        res = module._add_empty_result(fw, probelist, scan, session)
        self.assertCountEqual(res, probelist)

    @patch("api.scans.services.celery_brain")
    @patch("api.scans.services._add_empty_result")
    def test_add_empty_results(self, m_add_empty_result, m_celery_brain):
        m_scan, m_session = MagicMock(), MagicMock()
        fw1, fw2 = MagicMock(), MagicMock()
        fw1.file.sha256 = "sha256file1"
        fw1.file.mimetype = "mimetypefile1"
        fw2.file.sha256 = "sha256file2"
        fw2.file.mimetype = "mimetypefile2"
        fw_list = [fw1, fw2]
        probe1, probe2 = "Probe1", "Probe2"
        probelist = [probe1, probe2]
        m_add_empty_result.return_value = probelist
        m_celery_brain.mimetype_filter_scan_request = lambda x: x
        scan_request = module._create_scan_request(fw_list, probelist, True)
        res = module._add_empty_results(fw_list, scan_request,
                                        m_scan, m_session)
        self.assertCountEqual(res.to_dict().values(),
                              scan_request.to_dict().values())
    """
    @patch("api.scans.services.Scan")
    @patch("api.scans.services.session_transaction")
    def test_launch_asynchronous_nothing_to_do(self,
                                               m_session_transaction,
                                               m_Scan):
        m_session, m_scan = MagicMock(), MagicMock()
        m_session_transaction().__enter__.return_value = m_session
        m_scan.status = IrmaScanStatus.ready
        m_Scan.load_from_ext_id.return_value = m_scan
        module.launch_asynchronous("whatever")
        m_scan.set_status.assert_called_once_with(IrmaScanStatus.finished)

    @patch("api.scans.services._add_empty_result")
    @patch("api.scans.services.ftp_ctrl")
    @patch("api.scans.services.Scan")
    @patch("api.scans.services.session_transaction")
    def test_launch_asynchronous(self,
                                 m_session_transaction,
                                 m_Scan,
                                 m_ftp_ctrl,
                                 m_add_empty_result):
        m_scan, m_session = MagicMock(), MagicMock()
        fw1, fw2 = MagicMock(), MagicMock()
        file1, file2 = MagicMock(), MagicMock()
        pathf1, pathf2 = 'path-file1', 'path-file2'
        file1.path = pathf1
        file2.path = pathf2
        fw1.file.sha256 = "sha256file1"
        fw1.file.mimetype = "mimetypefile1"
        fw2.file.sha256 = "sha256file2"
        fw2.file.mimetype = "mimetypefile2"
        m_scan.files_web = [fw1, fw2]
        m_scan.files = [file1, file2]
        probe1, probe2 = "Probe1", "Probe2"
        probelist = [probe1, probe2]
        m_scan.get_probe_list.return_value = probelist
        m_add_empty_result.return_value = probelist
        m_session_transaction().__enter__.return_value = m_session
        m_scan.status = IrmaScanStatus.ready
        m_scan.mimetype_filtering = False
        m_Scan.load_from_ext_id.return_value = m_scan
        scanid = "scanid"
        module.launch_asynchronous(scanid)
        m_ftp_ctrl.upload_scan.assert_called_with(scanid, [pathf1, pathf2])
        m_scan.set_status.assert_called_once_with(IrmaScanStatus.uploaded)

    @patch("api.scans.services._add_empty_result")
    @patch("api.scans.services.ftp_ctrl")
    @patch("api.scans.services.Scan")
    @patch("api.scans.services.session_transaction")
    def test_launch_asynchronous_ftp_error(self,
                                           m_session_transaction,
                                           m_Scan,
                                           m_ftp_ctrl,
                                           m_add_empty_result):
        m_scan, m_session = MagicMock(), MagicMock()
        fw1, fw2 = MagicMock(), MagicMock()
        file1, file2 = MagicMock(), MagicMock()
        pathf1, pathf2 = 'path-file1', 'path-file2'
        file1.path = pathf1
        file2.path = pathf2
        fw1.file.sha256 = "sha256file1"
        fw1.file.mimetype = "mimetypefile1"
        fw2.file.sha256 = "sha256file2"
        fw2.file.mimetype = "mimetypefile2"
        m_scan.files_web = [fw1, fw2]
        m_scan.files = [file1, file2]
        probe1, probe2 = "Probe1", "Probe2"
        probelist = [probe1, probe2]
        m_scan.get_probe_list.return_value = probelist
        m_add_empty_result.return_value = probelist
        m_session_transaction().__enter__.return_value = m_session
        m_scan.status = IrmaScanStatus.ready
        m_scan.mimetype_filtering = False
        m_Scan.load_from_ext_id.return_value = m_scan
        scanid = "scanid"
        m_ftp_ctrl.upload_scan.side_effect = IrmaFtpError()
        module.launch_asynchronous(scanid)
        expected = IrmaScanStatus.error_ftp_upload
        m_scan.set_status.assert_called_once_with(expected)
    """
    @patch("api.scans.services.log")
    @patch("api.scans.services.FileExt")
    @patch("api.scans.services.session_transaction")
    def test_set_result_fw_not_found(self,
                                     m_session_transaction,
                                     m_FileExt,
                                     m_log):
        m_session = MagicMock()
        m_session_transaction().__enter__.return_value = m_session
        m_FileExt.load_from_ext_id.side_effect = IrmaDatabaseError
        with self.assertRaises(IrmaDatabaseError):
            module.set_result("filewebid", "probe", "result")

    @patch("api.scans.services.FileExt")
    @patch("api.scans.services.session_transaction")
    def test_set_result(self, m_session_transaction, m_FileExt):
        filewebid = "filewebid"
        probe = "probe"
        m_session = MagicMock()
        m_session_transaction().__enter__.return_value = m_session
        m_file_ext, pr1 = MagicMock(), MagicMock()
        pr1.doc = "ProbeResult"
        file1 = MagicMock()
        m_file_ext.file = file1
        m_file_ext.probe_results = [pr1]
        m_FileExt.load_from_ext_id.return_value = m_file_ext
        result = {'status': 1, 'type': "something"}
        module.set_result(filewebid, probe, result)
        m_file_ext.set_result.assert_called_once_with(probe, result)
        m_FileExt.load_from_ext_id.assert_called_with(filewebid,
                                                      session=m_session)

    @patch("api.scans.services.FileExt")
    @patch("api.scans.services.session_transaction")
    def test_handle_output_files_no_resubmit(self,
                                             m_session_transaction,
                                             m_FileExt):
        m_file_ext, m_session = MagicMock(), MagicMock()
        m_session_transaction().__enter__.return_value = m_session
        m_file_ext.scan.resubmit_files = True
        m_FileExt.load_from_ext_id.return_value = m_file_ext
        result = {}
        module.handle_output_files("filewebid", result)
        m_FileExt.load_from_ext_id.assert_called_once_with("filewebid",
                                                           m_session)

    @patch("api.scans.services.FileExt")
    @patch("api.scans.services.session_transaction")
    def test_handle_output_files_resubmit_False(self,
                                                m_session_transaction,
                                                m_FileExt):
        m_file_ext, m_session = MagicMock(), MagicMock()
        m_session_transaction().__enter__.return_value = m_session
        m_file_ext.scan.resubmit_files = False
        m_file_ext.depth = 0
        m_FileExt.load_from_ext_id.return_value = m_file_ext
        result = {'uploaded_files': {}}
        module.handle_output_files("filewebid", result)
        m_FileExt.load_from_ext_id.assert_called_once_with("filewebid",
                                                           m_session)

    @patch("api.scans.services._append_new_files_to_scan")
    @patch("api.scans.services.FileExt")
    @patch("api.scans.services.session_transaction")
    def test_handle_output_files_resubmit(self,
                                          m_session_transaction,
                                          m_FileExt,
                                          m_append_new_files_to_scan):
        m_file_ext, m_session = MagicMock(), MagicMock()
        m_session_transaction().__enter__.return_value = m_session
        m_file_ext.resubmit_files = True
        m_file_ext.depth = 0
        m_FileExt.load_from_ext_id.return_value = m_file_ext
        uploaded_files = {'filename': 'filehash'}
        result = {'uploaded_files': uploaded_files, 'name': 'probe_name'}
        fw1 = MagicMock()
        m_append_new_files_to_scan.return_value = [fw1]
        m_parentfile = MagicMock()
        m_file_ext.file = m_parentfile
        m_parentfile.children = []
        module.handle_output_files("filewebid", result)
        m_FileExt.load_from_ext_id.assert_called_once_with("filewebid",
                                                           m_session)
        m_append_new_files_to_scan.assert_called_once_with(
            m_file_ext.scan,
            uploaded_files,
            m_file_ext.fetch_probe_result(result['name']),
            m_file_ext.depth+1)
        self.assertCountEqual(m_parentfile.children, [fw1])

    @patch("api.scans.services._append_new_files_to_scan")
    @patch("api.scans.services.FileExt")
    @patch("api.scans.services.session_transaction")
    def test_handle_output_files_resubmit_none(self,
                                               m_session_transaction,
                                               m_FileExt,
                                               m_append_new_files_to_scan):
        m_file_ext, m_session = MagicMock(), MagicMock()
        m_session_transaction().__enter__.return_value = m_session
        m_file_ext.scan.resubmit_files = True
        m_file_ext.depth = 0
        m_FileExt.load_from_ext_id.return_value = m_file_ext
        result = {}
        fw1 = MagicMock()
        m_append_new_files_to_scan.return_value = [fw1]
        m_parentfile = MagicMock()
        m_parentfile.children = []
        m_file_ext.file = m_parentfile
        module.handle_output_files("filewebid",  result)
        m_FileExt.load_from_ext_id.assert_called_once_with("filewebid",
                                                           m_session)
        m_append_new_files_to_scan.assert_not_called()
        self.assertCountEqual(m_parentfile.children, [])

    @patch("api.scans.services._append_new_files_to_scan")
    @patch("api.scans.services.FileExt")
    @patch("api.scans.services.session_transaction")
    def test_handle_output_files_resubmit_level_ok(
            self,
            m_session_transaction,
            m_FileExt,
            m_append_new_files_to_scan):
        m_file_ext, m_session = MagicMock(), MagicMock()
        m_session_transaction().__enter__.return_value = m_session
        m_file_ext.resubmit_files = True
        m_file_ext.depth = 15
        m_FileExt.load_from_ext_id.return_value = m_file_ext
        uploaded_files = {'filename': 'filehash'}
        result = {'uploaded_files': uploaded_files, 'name': 'probe_name'}
        fw1 = MagicMock()
        m_append_new_files_to_scan.return_value = [fw1]
        m_parentfile = MagicMock()
        m_file_ext.file = m_parentfile
        m_parentfile.children = []
        module.handle_output_files("filewebid", result)
        m_FileExt.load_from_ext_id.assert_called_once_with("filewebid",
                                                           m_session)
        m_append_new_files_to_scan.assert_called_once_with(
            m_file_ext.scan,
            uploaded_files,
            m_file_ext.fetch_probe_result(result['name']),
            m_file_ext.depth+1)
        self.assertCountEqual(m_parentfile.children, [fw1])

    @patch("api.scans.services._append_new_files_to_scan")
    @patch("api.scans.services.FileExt")
    @patch("api.scans.services.session_transaction")
    def test_handle_output_files_resubmit_level_ok(
            self,
            m_session_transaction,
            m_FileExt,
            m_append_new_files_to_scan):
        m_file_ext, m_session = MagicMock(), MagicMock()
        m_session_transaction().__enter__.return_value = m_session
        m_file_ext.resubmit_files = True
        m_file_ext.depth = 16
        m_FileExt.load_from_ext_id.return_value = m_file_ext
        uploaded_files = {'filename': 'filehash'}
        result = {'uploaded_files': uploaded_files, 'name': 'probe_name'}
        fw1 = MagicMock()
        m_append_new_files_to_scan.return_value = [fw1]
        m_parentfile = MagicMock()
        m_file_ext.file = m_parentfile
        m_parentfile.children = []
        module.handle_output_files("filewebid", result)
        m_FileExt.load_from_ext_id.assert_called_once_with("filewebid",
                                                           m_session)
        m_append_new_files_to_scan.assert_not_called()
        self.assertCountEqual(m_parentfile.children, [])

    @patch("api.scans.services.session_query")
    def test_generate_csv_report_as_stream(self, m_session_query):
        m_session = MagicMock()
        m_scan = MagicMock()
        m_fe = MagicMock()

        m_session_query().__enter__.return_value = m_session
        m_session.merge.return_value = m_scan

        m_fe.file.md5 = "md5"
        m_fe.file.sha1 = "sha1"
        m_fe.file.sha256 = "sha256"
        m_fe.name = "filename"
        m_fe.file.timestamp_first_scan = "ts_first_scan"
        m_fe.file.timestamp_last_scan = "ts_last_scan"
        m_fe.file.size = "size"
        m_fe.status = "status"
        m_fe.submitter = "submitter"
        m_fe.get_probe_results.return_value = {
            "antivirus": {"av1": {"status": "result_av1"}},
            "external": {
                "VirusTotal": {"results": "result_vt"},
                # Ext1 should not appear in the result.
                "Ext1": {"results": "ext1"},
            },
            # Metadata should not appear in the result.
            "metadata": {"meta1": {"status": "result_meta1"}},
        }

        m_scan.date = "scan_date"
        m_scan.ip = "IP"
        m_scan.files_ext = [m_fe]

        # list function is only used there to retrieve all the information
        # return by the generator.
        # In this case, the parameter is not important as the scan variable
        # will be return by the `session.merge` function which is Mock to
        # return `m_scan`.
        actual = list(module.generate_csv_report_as_stream(None))
        expected = [
            (b"Date;MD5;SHA1;SHA256;Filename;First seen;Last seen;Size;Status;"
             b"Submitter;Submitter's IP address;av1;VirusTotal"),
            b"\r\n",
            (b"scan_date;md5;sha1;sha256;filename;ts_first_scan;ts_last_scan;"
             b"size;status;submitter;IP;result_av1;result_vt"),
            b"\r\n",
        ]

        self.assertEqual(actual, expected)
