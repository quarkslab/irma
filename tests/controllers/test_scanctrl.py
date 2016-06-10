from unittest import TestCase
from mock import MagicMock, patch

import frontend.controllers.scanctrl as module
from lib.irma.common.utils import IrmaScanStatus
from tempfile import TemporaryFile
from lib.irma.common.exceptions import IrmaValueError, IrmaTaskError, \
    IrmaDatabaseResultNotFound
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
