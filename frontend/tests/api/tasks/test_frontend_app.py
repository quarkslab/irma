from unittest import TestCase
from mock import patch, MagicMock
import api.tasks.frontend_app as module


class TestModuleFrontendApp(TestCase):

    def setUp(self):
        self.old_config = module.config
        self.config = MagicMock()
        self.frontend_config = dict()
        self.frontend_config["cron_clean_file_age"] = {
            "clean_fs_max_age": "1 week",
            "clean_fs_age_cron_hour": "0",
            "clean_fs_age_cron_minute": "0",
            "clean_fs_age_cron_day_of_week": "*",
        }
        self.frontend_config["cron_clean_file_size"] = {
            "clean_fs_max_size": "100 Mb",
            "clean_fs_size_cron_hour": "*",
            "clean_fs_size_cron_minute": "0",
            "clean_fs_size_cron_day_of_week": "*",
        }
        self.config.frontend_config = self.frontend_config
        module.config = self.config

    def tearDown(self):
        module.config = self.old_config
        del self.config

    @patch("api.tasks.frontend_app.celery")
    @patch("api.tasks.frontend_app.Scan")
    @patch("api.tasks.frontend_app.scan_ctrl")
    @patch("api.tasks.frontend_app.session_transaction")
    def test_scan_launch(self, m_session_transaction, m_scan_ctrl, m_Scan,
                         m_celery):
        m_session = MagicMock()
        m_session_transaction().__enter__.return_value = m_session
        scan = MagicMock()
        m_Scan.load_from_ext_id.return_value = scan
        m_scanr = MagicMock()
        m_scanr.nb_files = 10
        m_add_empty_results = MagicMock()
        m_add_empty_results.return_value = m_scanr
        m_scan_ctrl._add_empty_results = m_add_empty_results
        scan_id = "whatever"
        module.scan_launch(scan_id)
        scan.set_status.assert_called_with(module.IrmaScanStatus.launched)
        m_celery.group.assert_called()

    @patch("api.tasks.frontend_app.celery")
    @patch("api.tasks.frontend_app.Scan")
    @patch("api.tasks.frontend_app.scan_ctrl")
    @patch("api.tasks.frontend_app.session_transaction")
    def test_scan_launch_no_files(self, m_session_transaction, m_scan_ctrl,
                                  m_Scan, m_celery):
        m_session = MagicMock()
        m_session_transaction().__enter__.return_value = m_session
        scan = MagicMock()
        m_Scan.load_from_ext_id.return_value = scan
        m_scanr = MagicMock()
        m_scanr.nb_files = 0
        m_add_empty_results = MagicMock()
        m_add_empty_results.return_value = m_scanr
        m_scan_ctrl._add_empty_results = m_add_empty_results
        scan_id = "whatever"
        module.scan_launch(scan_id)
        scan.set_status.assert_called_with(module.IrmaScanStatus.finished)
        m_celery.group.assert_not_called()

    @patch("api.tasks.frontend_app.celery")
    @patch("api.tasks.frontend_app.Scan")
    @patch("api.tasks.frontend_app.scan_ctrl")
    @patch("api.tasks.frontend_app.session_transaction")
    def test_scan_launch_raises(self, m_session_transaction, m_scan_ctrl,
                                m_Scan, m_celery):
        m_session = MagicMock()
        m_session_transaction().__enter__.return_value = m_session
        scan = MagicMock()
        m_Scan.load_from_ext_id.return_value = scan
        m_scanr = MagicMock()
        m_scanr.nb_files = 0
        m_add_empty_results = MagicMock()
        m_add_empty_results.side_effect = module.IrmaDatabaseError
        m_scan_ctrl._add_empty_results = m_add_empty_results
        scan_id = "whatever"
        module.scan_launch(scan_id)
        scan.set_status.assert_called_with(module.IrmaScanStatus.error)
        m_celery.group.assert_not_called()

    @patch("api.tasks.frontend_app.celery_brain")
    @patch("api.tasks.frontend_app.FileExt")
    @patch("api.tasks.frontend_app.ftp_ctrl")
    @patch("api.tasks.frontend_app.session_transaction")
    def test_scan_launch_file_ext(self, m_session_transaction,
                                  m_ftp_ctrl, m_FileExt, m_celery_brain):
        m_session = MagicMock()
        m_session_transaction().__enter__.return_value = m_session
        file_ext = MagicMock()
        m_FileExt.load_from_ext_id.return_value = file_ext
        module.scan_launch_file_ext("whatever")
        m_ftp_ctrl.upload_file.assert_called_with("whatever",
                                                  file_ext.file.path)
        m_celery_brain.scan_launch.\
            assert_called_with("whatever",
                               file_ext.probes,
                               file_ext.scan.external_id)
        file_ext.scan.set_status.assert_not_called()

    @patch("api.tasks.frontend_app.celery_brain")
    @patch("api.tasks.frontend_app.FileExt")
    @patch("api.tasks.frontend_app.ftp_ctrl")
    @patch("api.tasks.frontend_app.session_transaction")
    def test_scan_launch_file_ext_ftp_error(self, m_session_transaction,
                                            m_ftp_ctrl, m_FileExt,
                                            m_celery_brain):
        m_session = MagicMock()
        m_session_transaction().__enter__.return_value = m_session
        file_ext = MagicMock()
        m_FileExt.load_from_ext_id.return_value = file_ext
        m_ftp_ctrl.upload_file.side_effect = module.IrmaFtpError
        module.scan_launch_file_ext("whatever")
        m_celery_brain.scan_launch.assert_not_called()
        file_ext.scan.set_status.assert_called_with(
                module.IrmaScanStatus.error_ftp_upload)

    @patch("api.tasks.frontend_app.celery_brain")
    @patch("api.tasks.frontend_app.FileExt")
    @patch("api.tasks.frontend_app.ftp_ctrl")
    @patch("api.tasks.frontend_app.session_transaction")
    def test_scan_launch_file_ext_other_error(self, m_session_transaction,
                                              m_ftp_ctrl, m_FileExt,
                                              m_celery_brain):
        m_session = MagicMock()
        m_session_transaction().__enter__.return_value = m_session
        file_ext = MagicMock()
        m_FileExt.load_from_ext_id.return_value = file_ext
        m_ftp_ctrl.upload_file.side_effect = ValueError
        module.scan_launch_file_ext("whatever")
        m_celery_brain.scan_launch.assert_not_called()
        file_ext.scan.set_status.assert_not_called()

    @patch("api.tasks.frontend_app.scan_ctrl")
    def test_scan_result(self, m_scan_ctrl):
        module.scan_result("whatever", "probe", "result")
        m_scan_ctrl.handle_output_files.assert_called_with("whatever",
                                                           "result")
        m_scan_ctrl.set_result.assert_called_with("whatever", "probe",
                                                  "result")

    @patch("api.tasks.frontend_app.scan_ctrl")
    def test_scan_result_raises(self, m_scan_ctrl):
        m_scan_ctrl.handle_output_files.side_effect = module.IrmaDatabaseError
        with self.assertRaises(module.IrmaDatabaseError):
            module.scan_result("whatever", "probe", "result")
        m_scan_ctrl.set_result.assert_not_called()

    @patch("api.files.services.remove_files")
    def test_clean_fs_age(self, m_remove_files):
        m_remove_files.return_value = 1684
        res = module.clean_fs_age()
        m_remove_files.assert_called_with(7*24*60*60)
        self.assertEqual(res, 1684)

    @patch("api.tasks.frontend_app.scan_ctrl")
    def test_scan_result_error(self, m_scan_ctrl):
        result = dict()
        module.scan_result_error("parent", "whatever", "probe", result)
        m_scan_ctrl.handle_output_files.assert_called_with("whatever",
                                                           result,
                                                           error_case=True)
        m_scan_ctrl.set_result.assert_called_with("whatever", "probe",
                                                  result)
        self.assertEqual(result["status"], -1)
        self.assertEqual(result["error"], "Error raised during result insert")

    @patch("api.files.services.remove_files")
    def test_clean_fs_age_disabled(self, m_remove_files):
        self.frontend_config["cron_clean_file_age"][
            "clean_fs_max_age"] = "0"
        res = module.clean_fs_age()
        m_remove_files.assert_not_called()
        self.assertEqual(res, 0)

    @patch("api.files.services.remove_files")
    def test_clean_fs_age_raises1(self, m_remove_files):
        m_remove_files.side_effect = module.IrmaDatabaseError
        module.clean_fs_age()

    @patch("api.files.services.remove_files")
    def test_clean_fs_age_raises2(self, m_remove_files):
        m_remove_files.side_effect = module.IrmaFileSystemError
        module.clean_fs_age()

    @patch("api.files.services.remove_files")
    def test_clean_fs_age_raises3(self, m_remove_files):
        m_remove_files.side_effect = ValueError
        with self.assertRaises(ValueError):
            module.clean_fs_age()

    @patch("api.files.services.remove_files_size")
    def test_clean_size(self, m_remove_files_size):
        m_remove_files_size.return_value = 2654
        res = module.clean_fs_size()
        m_remove_files_size.assert_called_with(100*1024*1024)
        self.assertEqual(res, 2654)

    @patch("api.files.services.remove_files_size")
    def test_clean_fs_size_disabled(self, m_remove_files_size):
        self.frontend_config["cron_clean_file_size"][
            "clean_fs_max_size"] = "0"
        res = module.clean_fs_size()
        m_remove_files_size.assert_not_called()
        self.assertEqual(res, 0)

    @patch("api.files.services.remove_files_size")
    def test_clean_fs_size_raises1(self, m_remove_files_size):
        m_remove_files_size.side_effect = module.IrmaDatabaseError
        module.clean_fs_size()

    @patch("api.files.services.remove_files_size")
    def test_clean_fs_size_raises2(self, m_remove_files_size):
        m_remove_files_size.side_effect = module.IrmaFileSystemError
        module.clean_fs_size()

    @patch("api.files.services.remove_files_size")
    def test_clean_fs_size_raises3(self, m_remove_files_size):
        m_remove_files_size.side_effect = ValueError
        with self.assertRaises(ValueError):
            module.clean_fs_size()
