from unittest import TestCase
from mock import MagicMock, patch

import frontend.controllers.scanctrl as module
from lib.irma.common.utils import IrmaScanStatus
from tempfile import TemporaryFile
from lib.irma.common.exceptions import IrmaValueError, IrmaTaskError, \
    IrmaDatabaseResultNotFound, IrmaFtpError
from lib.irma.common.utils import IrmaReturnCode


class TestModuleScanctrl(TestCase):

    def setUp(self):
        self.old_File = module.File
        self.old_Scan = module.Scan
        self.old_build_sha256_path = module.build_sha256_path
        self.old_celery_brain = module.celery_brain
        self.File = MagicMock()
        self.Scan = MagicMock()

        self.build_sha256_path = MagicMock()
        self.celery_brain = MagicMock()
        module.File = self.File
        module.Scan = self.Scan
        module.build_sha256_path = self.build_sha256_path
        module.celery_brain = self.celery_brain

    def tearDown(self):
        module.File = self.old_File
        module.Scan = self.old_Scan
        module.build_sha256_path = self.old_build_sha256_path
        module.celery_brain = self.old_celery_brain
        del self.File
        del self.Scan
        del self.build_sha256_path
        del self.celery_brain

    def test001_add_files(self):
        fobj = TemporaryFile()
        filename = "n_test"
        scan, session = MagicMock(), MagicMock()
        function = "frontend.controllers.scanctrl.IrmaScanStatus.filter_status"
        with patch(function) as mock:
            scan.status = IrmaScanStatus.empty
            module.add_files(scan, {filename: fobj}, session)
        self.assertTrue(mock.called)
        self.assertEqual(mock.call_args,
                         ((scan.status, IrmaScanStatus.empty,
                           IrmaScanStatus.ready),))
        self.File.load_from_sha256.assert_called_once()
        self.build_sha256_path.assert_called_once()
        fobj.close()

    def test002_check_probe(self):
        scan, session = MagicMock(), MagicMock()
        scan.status = IrmaScanStatus.ready
        probelist = ['probe1', 'probe2']
        all_probelist = ['probe1', 'probe2', 'probe3']
        scan.set_probelist.return_value = None
        self.celery_brain.probe_list.return_value = all_probelist
        module.check_probe(scan, probelist, session)
        self.assertTrue(scan.set_probelist.called)
        scan.set_probelist.assert_called_once_with(probelist)

    def test003_check_probe_None(self):
        scan, session = MagicMock(), MagicMock()
        scan.status = IrmaScanStatus.ready
        probelist = None
        all_probelist = ['probe1', 'probe2', 'probe3']
        scan.set_probelist.return_value = None
        self.celery_brain.probe_list.return_value = all_probelist
        module.check_probe(scan, probelist, session)
        self.assertTrue(scan.set_probelist.called)
        scan.set_probelist.assert_called_once_with(all_probelist)

    def test004_check_probe_unknown_probe(self):
        scan, session = MagicMock(), MagicMock()
        scan.status = IrmaScanStatus.ready
        probelist = ['probe1', 'probe2', 'probe6']
        all_probelist = ['probe1', 'probe2', 'probe3']
        scan.set_probelist.return_value = None
        self.celery_brain.probe_list.return_value = all_probelist
        with self.assertRaises(IrmaValueError) as context:
            module.check_probe(scan, probelist, session)
        self.assertFalse(scan.set_probelist.called)
        self.assertEquals(str(context.exception), "probe probe6 unknown")

    def test005_cancel_status_empty(self):
        scan, session = MagicMock(), MagicMock()
        scan.status = IrmaScanStatus.empty
        res = module.cancel(scan, session)
        self.assertIsNone(res)
        scan.set_status.assert_called_once_with(IrmaScanStatus.cancelled)

    def test006_cancel_status_ready(self):
        scan, session = MagicMock(), MagicMock()
        scan.status = IrmaScanStatus.ready
        res = module.cancel(scan, session)
        self.assertIsNone(res)
        scan.set_status.assert_called_once_with(IrmaScanStatus.cancelled)

    def test007_cancel_status_uploaded(self):
        scan, session = MagicMock(), MagicMock()
        scan.status = IrmaScanStatus.uploaded
        label = IrmaScanStatus.label[scan.status]
        expected = "can not cancel scan in {} status".format(label)
        with self.assertRaises(IrmaValueError) as context:
            module.cancel(scan, session)
        self.assertEqual(str(context.exception), expected)

    def test008_cancel_status_launched_ok(self):
        scan, session = MagicMock(), MagicMock()
        scan.status = IrmaScanStatus.launched
        retcode = IrmaReturnCode.success
        cancel_res = {'cancel_details': "details"}
        self.celery_brain.scan_cancel.return_value = (retcode, cancel_res)
        res = module.cancel(scan, session)
        self.assertEqual(res, cancel_res['cancel_details'])
        scan.set_status.assert_called_once_with(IrmaScanStatus.cancelled)

    def test008_cancel_status_launched_status_processed(self):
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

    def test008_cancel_status_launched_status_error(self):
        scan, session = MagicMock(), MagicMock()
        scan.status = IrmaScanStatus.error_ftp_upload
        res = module.cancel(scan, session)
        self.assertIsNone(res)
        scan.set_status.assert_not_called()

    def test008_cancel_status_launched_brain_error(self):
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

    def test009_cancel_status_processed(self):
        scan, session = MagicMock(), MagicMock()
        scan.status = IrmaScanStatus.processed
        label = IrmaScanStatus.label[scan.status]
        expected = "can not cancel scan in {} status".format(label)
        with self.assertRaises(IrmaValueError) as context:
            module.cancel(scan, session)
        self.assertEqual(str(context.exception), expected)

    def test010_cancel_status_flushed(self):
        scan, session = MagicMock(), MagicMock()
        scan.status = IrmaScanStatus.flushed
        label = IrmaScanStatus.label[scan.status]
        expected = "can not cancel scan in {} status".format(label)
        with self.assertRaises(IrmaValueError) as context:
            module.cancel(scan, session)
        self.assertEqual(str(context.exception), expected)

    def test011_cancel_status_cancelling(self):
        scan, session = MagicMock(), MagicMock()
        scan.status = IrmaScanStatus.cancelling
        label = IrmaScanStatus.label[scan.status]
        expected = "can not cancel scan in {} status".format(label)
        with self.assertRaises(IrmaValueError) as context:
            module.cancel(scan, session)
        self.assertEqual(str(context.exception), expected)

    def test012_cancel_status_cancelled(self):
        scan, session = MagicMock(), MagicMock()
        scan.status = IrmaScanStatus.cancelled
        label = IrmaScanStatus.label[scan.status]
        expected = "can not cancel scan in {} status".format(label)
        with self.assertRaises(IrmaValueError) as context:
            module.cancel(scan, session)
        self.assertEqual(str(context.exception), expected)

    def test013_set_launched_status_uploaded(self):
        scan = MagicMock()
        scan.status = IrmaScanStatus.uploaded
        self.Scan.load_from_ext_id.return_value = scan
        module.set_launched("whatever", "whatever")
        scan.set_status.assert_called_with(IrmaScanStatus.launched)

    def test014_set_launched_status_not_uploaded(self):
        scan = MagicMock()
        scan.status = IrmaScanStatus.finished
        self.Scan.load_from_ext_id.return_value = scan
        module.set_launched("whatever", "whatever")
        self.assertEqual(scan.status, IrmaScanStatus.finished)

    @patch("frontend.controllers.scanctrl.sha256sum")
    def test015_new_file_existing(self, m_sha256sum):
        m_file = MagicMock()
        m_file.path = "whatever"
        self.File.load_from_sha256.return_value = m_file
        fobj, session = MagicMock(), MagicMock()
        res = module._new_file(fobj, session)
        self.assertEqual(res, m_file)

    @patch("frontend.controllers.scanctrl.sha256sum")
    @patch("frontend.controllers.scanctrl.save_to_file")
    def test016_new_file_existing_deleted(self, m_save_to_file, m_sha256sum):
        m_file = MagicMock()
        self.File.load_from_sha256.return_value = m_file
        fobj, session = MagicMock(), MagicMock()
        path = "testpath"
        self.build_sha256_path.return_value = path
        m_file.path = None
        module._new_file(fobj, session)
        m_save_to_file.assert_called_once_with(fobj, path)

    @patch("frontend.controllers.scanctrl.md5sum")
    @patch("frontend.controllers.scanctrl.sha1sum")
    @patch("frontend.controllers.scanctrl.sha256sum")
    @patch("frontend.controllers.scanctrl.Magic")
    @patch("frontend.controllers.scanctrl.save_to_file")
    def test017_new_file_not_existing(self, m_save_to_file, m_magic,
                                      m_sha256sum, m_sha1sum, m_md5sum):
        self.File.load_from_sha256.side_effect = IrmaDatabaseResultNotFound
        fobj, session = MagicMock(), MagicMock()
        path = "testpath"
        self.build_sha256_path.return_value = path
        module._new_file(fobj, session)
        m_md5sum.assert_called_once_with(fobj)
        m_sha1sum.assert_called_once_with(fobj)
        m_sha256sum.assert_called_once_with(fobj)
        m_magic.assert_called()
        self.File.assert_called()

    def test018_update_ref_no_prev(self):
        m_fw, m_file, m_pr = MagicMock(), MagicMock(), MagicMock()
        m_probe = MagicMock()
        probe = MagicMock()
        probename = "probe1"
        probe.name = probename
        m_probe.name = probe
        m_file.ref_results = []
        m_pr.name = "probe2"
        module._update_ref_results(m_fw, m_file, m_pr)
        self.assertItemsEqual(m_file.ref_results, [m_pr])

    def test019_update_ref_prev(self):
        m_fw, m_file = MagicMock(), MagicMock()
        m_pr_new, m_pr_old = MagicMock(), MagicMock()
        m_probe = MagicMock()
        probe = MagicMock()
        probename = "probe1"
        probe.name = probename
        m_probe.name = probe
        m_pr_old.name = "probe1"
        m_pr_new.name = "probe1"
        m_file.ref_results = [m_pr_old]
        module._update_ref_results(m_fw, m_file, m_pr_new)
        self.assertItemsEqual(m_file.ref_results, [m_pr_new])

    @patch("frontend.controllers.scanctrl.log")
    def test020_update_ref_error(self, m_log):
        m_fw, m_file, m_pr = MagicMock(), MagicMock(), MagicMock()
        m_probe = MagicMock()
        probe = MagicMock()
        probename = "probe1"
        probe.name = probename
        m_probe.name = probe
        m_pr.name = "probe1"
        m_file.ref_results = [m_pr, m_pr]
        module._update_ref_results(m_fw, m_file, m_pr)
        self.assertItemsEqual(m_file.ref_results, [m_pr, m_pr])
        m_log.error.called_once()

    def test021_fetch_probe_results(self):
        m_fw, m_pr = MagicMock(), MagicMock()
        probename = "probe1"
        m_pr.name = probename
        m_fw.probe_results = [m_pr]
        res = module._fetch_probe_result(m_fw, probename)
        self.assertEqual(res, m_pr)

    def test021b_fetch_probe_results_none(self):
        m_fw, m_pr = MagicMock(), MagicMock()
        probename = "probe1"
        m_pr.name = probename
        m_fw.probe_results = []
        res = module._fetch_probe_result(m_fw, probename)
        self.assertIsNone(res)

    @patch("frontend.controllers.scanctrl.log")
    def test022_resubmit_new_files_error(self, m_log):
        m_scan, m_parent_file = MagicMock(), MagicMock()
        m_resubmit_fws, m_session = MagicMock(), MagicMock()
        hash_uploaded = "whatever"
        m_parent_file.files_web = []
        module._resubmit_files(m_scan, m_parent_file, m_resubmit_fws,
                               hash_uploaded, m_session)
        m_log.error.assert_called_once()
        self.celery_brain.scan_launch.assert_not_called()

    @patch("frontend.controllers.scanctrl.log")
    def test023_resubmit_new_files_no_new_file(self, m_log):
        m_scan, m_parent_file = MagicMock(), MagicMock()
        m_session = MagicMock()
        m_fw = MagicMock()
        hash_uploaded = ["whatever"]
        m_fw.file.sha256 = hash_uploaded[0]
        m_resubmit_fws = [m_fw]
        m_parent_file.files_web = [m_fw]
        module._resubmit_files(m_scan, m_parent_file, m_resubmit_fws,
                               hash_uploaded, m_session)
        self.celery_brain.scan_launch.assert_not_called()

    @patch("frontend.controllers.scanctrl.log")
    def test024_resubmit_new_files_new_file(self, m_log):
        m_scan, m_parent_file = MagicMock(), MagicMock()
        m_session = MagicMock()
        m_fw = MagicMock()
        hash_uploaded = ["whatever"]
        m_fw.file.sha256 = "anotherthing"
        m_resubmit_fws = [m_fw]
        m_parent_file.files_web = [m_fw]
        module._resubmit_files(m_scan, m_parent_file, m_resubmit_fws,
                               hash_uploaded, m_session)
        self.celery_brain.scan_launch.assert_called()

    @patch("frontend.controllers.scanctrl._new_fileweb")
    @patch("frontend.controllers.scanctrl.ftp_ctrl")
    def test025_append_new_files(self, m_ftpctrl, m_new_fw):
        m_scan, m_session = MagicMock(), MagicMock()
        filename = "filename"
        filehash = "filehash"
        uploaded_files = {filename: filehash}
        m_fobj = MagicMock()
        m_ftpctrl.download_file_data.return_value = m_fobj
        module._append_new_files_to_scan(m_scan, uploaded_files, m_session)
        m_download = m_ftpctrl.download_file_data
        m_download.assert_called_once_with(m_scan.external_id, filehash)
        m_new_fw.assert_called_once_with(m_scan, filename, m_fobj, m_session)

    def test026_sanitize_res(self):
        pattern = u"\u0000test" + "\x00"
        pattern_expected = "test"
        dic_key = "te.st$key"
        dic_expected = "te_stkey"
        dic = {'unicode': unicode(pattern),
               'list': [pattern],
               'dict': {dic_key: pattern},
               'else': "else"}
        expected = {'unicode': pattern_expected,
                    'list': [pattern_expected],
                    'dict': {dic_expected: pattern_expected},
                    'else': "else"}
        res = module._sanitize_res(dic)
        self.assertItemsEqual(res.values(), expected.values())

    def test027_add_empty_result_refresult(self):
        fw, scan, session = MagicMock(), MagicMock(), MagicMock()
        pr1, pr2 = MagicMock(), MagicMock()
        probe1, probe2 = "Probe1", "Probe2"
        probelist = [probe1, probe2]
        pr1.name = probe1
        pr2.name = probe2
        scan.force = False
        fw.file.ref_results = [pr1, pr2]
        fw.probe_results = []
        module._add_empty_result(fw, probelist, scan, session)
        self.assertItemsEqual(fw.probe_results, [pr1, pr2])

    @patch("frontend.controllers.scanctrl._fetch_known_results")
    def test027_add_empty_result_knownresult(self, m_fetch_known_results):
        fw, scan, session = MagicMock(), MagicMock(), MagicMock()
        pr1, pr2 = MagicMock(), MagicMock()
        probe1, probe2 = "Probe1", "Probe2"
        probelist = [probe1, probe2]
        pr1.name = probe1
        pr2.name = probe2
        scan.force = True
        m_fetch_known_results.return_value = [pr1, pr2]
        fw.probe_results = []
        module._add_empty_result(fw, probelist, scan, session)
        self.assertItemsEqual(fw.probe_results, [pr1, pr2])

    @patch("frontend.controllers.scanctrl.ProbeResult")
    def test028_add_empty_result_noresult(self, m_ProbeResult):
        fw, scan, session = MagicMock(), MagicMock(), MagicMock()
        probe1, probe2 = "Probe1", "Probe2"
        probelist = [probe1, probe2]
        scan.force = True
        fw.probe_results = []
        res = module._add_empty_result(fw, probelist, scan, session)
        self.assertItemsEqual(res, probelist)

    @patch("frontend.controllers.scanctrl.FileWeb")
    def test029_fetch_known_results(self, m_FileWeb):
        m_scan, m_file, m_session = MagicMock(), MagicMock(), MagicMock()
        m_scan.id = "scanid"
        m_file.id = "fileid"
        fw1 = MagicMock()
        m_FileWeb.load_by_scanid_fileid.return_value = [fw1, fw1]
        res = module._fetch_known_results(m_file, m_scan, m_session)
        self.assertItemsEqual(res, fw1.probe_results)

    @patch("frontend.controllers.scanctrl.braintasks")
    @patch("frontend.controllers.scanctrl._add_empty_result")
    def test030_add_empty_results(self, m_add_empty_result, m_braintasks):
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
        m_braintasks.mimetype_filter_scan_request = lambda x: x
        scan_request = module._create_scan_request(fw_list, probelist, True)
        res = module._add_empty_results(fw_list, scan_request,
                                        m_scan, m_session)
        self.assertItemsEqual(res.to_dict().values(),
                              scan_request.to_dict().values())

    @patch("frontend.controllers.scanctrl.log")
    def test031_fetch_probe_results_error(self, m_log):
        fw, pr = MagicMock(), MagicMock()
        pr.name = "Probe1"
        fw.probe_results = [pr, pr]
        module._fetch_probe_result(fw, pr.name)
        m_log.error.assert_called_once()

    @patch("frontend.controllers.scanctrl.Scan")
    @patch("frontend.controllers.scanctrl.session_transaction")
    def test032_launch_asynchronous_nothing_to_do(self,
                                                  m_session_transaction,
                                                  m_Scan):
        m_session, m_scan = MagicMock(), MagicMock()
        m_session_transaction().__enter__.return_value = m_session
        m_scan.status = IrmaScanStatus.ready
        m_Scan.load_from_ext_id.return_value = m_scan
        module.launch_asynchronous("whatever")
        m_scan.set_status.assert_called_once_with(IrmaScanStatus.finished)

    @patch("frontend.controllers.scanctrl._add_empty_result")
    @patch("frontend.controllers.scanctrl.ftp_ctrl")
    @patch("frontend.controllers.scanctrl.Scan")
    @patch("frontend.controllers.scanctrl.session_transaction")
    def test033_launch_asynchronous(self,
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

    @patch("frontend.controllers.scanctrl._add_empty_result")
    @patch("frontend.controllers.scanctrl.ftp_ctrl")
    @patch("frontend.controllers.scanctrl.Scan")
    @patch("frontend.controllers.scanctrl.session_transaction")
    def test034_launch_asynchronous_ftp_error(self,
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

    @patch("frontend.controllers.scanctrl.log")
    @patch("frontend.controllers.scanctrl.Scan")
    @patch("frontend.controllers.scanctrl.session_transaction")
    def test035_set_result_fw_not_found(self,
                                        m_session_transaction,
                                        m_Scan,
                                        m_log):
        m_scan, m_session = MagicMock(), MagicMock()
        m_session_transaction().__enter__.return_value = m_session
        m_scan.get_filewebs_by_sha256.return_value = []
        m_Scan.load_from_ext_id.return_value = m_scan
        module.set_result("scanid", "filehash", "probe", "result")
        m_log.error.assert_called_once()

    @patch("frontend.controllers.scanctrl._update_ref_results")
    @patch("frontend.controllers.scanctrl._fetch_probe_result")
    @patch("frontend.controllers.scanctrl.Scan")
    @patch("frontend.controllers.scanctrl.session_transaction")
    def test036_set_result(self,
                           m_session_transaction,
                           m_Scan,
                           m_fetch_pr,
                           m_update_ref_res):
        scanid = "scanid"
        filehash = "filehash"
        probe = "probe"
        m_scan, m_session = MagicMock(), MagicMock()
        m_session_transaction().__enter__.return_value = m_session
        fw1, pr1 = MagicMock(), MagicMock()
        pr1.doc = "ProbeResult"
        file1 = MagicMock()
        fw1.file = file1
        fw1.probe_results = [pr1]
        m_scan.get_filewebs_by_sha256.return_value = [fw1]
        m_Scan.load_from_ext_id.return_value = m_scan
        result = {'status': 1, 'type': "something"}
        m_fetch_pr.return_value = pr1
        module.set_result(scanid, filehash, probe, result)
        m_fetch_pr.assert_called_once_with(fw1, probe)
        m_update_ref_res.assert_called_once_with(fw1, file1, pr1)
        m_Scan.load_from_ext_id.assert_called_with(scanid,
                                                   session=m_session)

    @patch("frontend.controllers.scanctrl.File")
    @patch("frontend.controllers.scanctrl.Scan")
    @patch("frontend.controllers.scanctrl.session_transaction")
    def test037_handle_output_files_no_resubmit(self,
                                                m_session_transaction,
                                                m_Scan,
                                                m_File):
        m_scan, m_session = MagicMock(), MagicMock()
        m_session_transaction().__enter__.return_value = m_session
        m_scan.resubmit_files = True
        m_Scan.load_from_ext_id.return_value = m_scan
        result = {}
        module.handle_output_files("scanid", "parent_file_hash",
                                   "probe", result)
        m_Scan.load_from_ext_id.assert_called_once_with("scanid",
                                                        session=m_session)

    @patch("frontend.controllers.scanctrl.File")
    @patch("frontend.controllers.scanctrl.Scan")
    @patch("frontend.controllers.scanctrl.session_transaction")
    def test038_handle_output_files_resubmit_False(self,
                                                   m_session_transaction,
                                                   m_Scan,
                                                   m_File):
        m_scan, m_session = MagicMock(), MagicMock()
        m_session_transaction().__enter__.return_value = m_session
        m_scan.resubmit_files = False
        m_Scan.load_from_ext_id.return_value = m_scan
        result = {'uploaded_files': []}
        module.handle_output_files("scanid", "parent_file_hash",
                                   "probe", result)
        m_Scan.load_from_ext_id.assert_called_once_with("scanid",
                                                        session=m_session)

    @patch("frontend.controllers.scanctrl._filter_children")
    @patch("frontend.controllers.scanctrl._append_new_files_to_scan")
    @patch("frontend.controllers.scanctrl.File")
    @patch("frontend.controllers.scanctrl.Scan")
    @patch("frontend.controllers.scanctrl.session_transaction")
    def test039_handle_output_files_resubmit(self,
                                             m_session_transaction,
                                             m_Scan,
                                             m_File,
                                             m_append_new_files_to_scan,
                                             m_filter_children):
        m_scan, m_session = MagicMock(), MagicMock()
        m_session_transaction().__enter__.return_value = m_session
        m_scan.resubmit_files = True
        m_Scan.load_from_ext_id.return_value = m_scan
        uploaded_files = {'filename': 'filehash'}
        result = {'uploaded_files': uploaded_files}
        fw1 = MagicMock()
        m_append_new_files_to_scan.return_value = [fw1]
        m_parentfile = MagicMock()
        m_parentfile.children = []
        m_filter_children.return_value = uploaded_files
        m_File.load_from_sha256.return_value = m_parentfile
        module.handle_output_files("scanid", "parent_file_hash",
                                   "probe", result)
        m_Scan.load_from_ext_id.assert_called_once_with("scanid",
                                                        session=m_session)
        m_append_new_files_to_scan.assert_called_once_with(m_scan,
                                                           uploaded_files,
                                                           m_session)
        self.assertItemsEqual(m_parentfile.children, [fw1])

    @patch("frontend.controllers.scanctrl._filter_children")
    @patch("frontend.controllers.scanctrl._append_new_files_to_scan")
    @patch("frontend.controllers.scanctrl.File")
    @patch("frontend.controllers.scanctrl.Scan")
    @patch("frontend.controllers.scanctrl.session_transaction")
    def test040_handle_output_files_resubmit_none(self,
                                                  m_session_transaction,
                                                  m_Scan,
                                                  m_File,
                                                  m_append_new_files_to_scan,
                                                  m_filter_children):
        m_scan, m_session = MagicMock(), MagicMock()
        m_session_transaction().__enter__.return_value = m_session
        m_scan.resubmit_files = True
        m_Scan.load_from_ext_id.return_value = m_scan
        uploaded_files = {}
        result = {'uploaded_files': uploaded_files}
        fw1 = MagicMock()
        m_append_new_files_to_scan.return_value = [fw1]
        m_parentfile = MagicMock()
        m_parentfile.children = []
        m_filter_children.return_value = {}
        m_File.load_from_sha256.return_value = m_parentfile
        module.handle_output_files("scanid", "parent_file_hash",
                                   "probe", result)
        m_Scan.load_from_ext_id.assert_called_once_with("scanid",
                                                        session=m_session)
        m_append_new_files_to_scan.assert_not_called()
        self.assertItemsEqual(m_parentfile.children, [])
