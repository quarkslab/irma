from unittest import TestCase
from mock import patch, MagicMock
import api.tasks.frontend_app as module


class TestModuleFrontendApp(TestCase):

    def setUp(self):
        self.old_config = module.config
        self.config = MagicMock()
        self.frontend_config = dict()
        self.frontend_config["cron_clean_file_age"] = {
            "clean_db_file_max_age": 2,
            "clean_db_cron_hour": "0",
            "clean_db_cron_minute": "0",
            "clean_db_cron_day_of_week": "*",
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

    @patch("api.files.services.remove_files")
    def test_clean_max_age(self, m_remove_files):
        m_remove_files.return_value = 1684
        res = module.clean_db()
        m_remove_files.assert_called_with(2*24*60*60)
        self.assertEqual(res, 1684)

    @patch("api.files.services.remove_files")
    def test_clean_max_age_disabled(self, m_remove_files):
        self.frontend_config["cron_clean_file_age"][
            "clean_db_file_max_age"] = 0
        res = module.clean_db()
        m_remove_files.assert_not_called()
        self.assertEqual(res, 0)

    @patch("api.files.services.remove_files_size")
    def test_clean_size(self, m_remove_files_size):
        m_remove_files_size.return_value = 2654
        res = module.clean_fs_size()
        m_remove_files_size.assert_called_with(100*1024*1024)
        self.assertEqual(res, 2654)

    @patch("api.files.services.remove_files_size")
    def test_clean_size_disabled(self, m_remove_files_size):
        self.frontend_config["cron_clean_file_size"][
            "clean_fs_max_size"] = "0"
        res = module.clean_fs_size()
        m_remove_files_size.assert_not_called()
        self.assertEqual(res, 0)
