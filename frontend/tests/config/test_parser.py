import config.parser as module
from unittest import TestCase
from random import randint
from mock import MagicMock, patch


class TestConfigParser(TestCase):

    @patch("config.parser.common_celery_options")
    @patch("config.parser.frontend_config")
    def test_get_celery_options(self, m_config,
                                m_common_celery_options):
        concurrency = randint(0, 50)
        soft_time_limit = randint(10, 100)
        time_limit = randint(10, 100)
        beat_schedule = "whatever"
        m_config.celery_options.concurrency = concurrency
        m_config.celery_options.soft_time_limit = soft_time_limit
        m_config.celery_options.time_limit = time_limit
        m_config.celery_options.beat_schedule = beat_schedule
        options = module.common_celery_options("app",
                                               "app_name",
                                               concurrency,
                                               soft_time_limit,
                                               time_limit)
        options.append("--beat")
        options.append("--schedule={}".format(beat_schedule))
        self.assertEqual(options, module.get_celery_options("app", "appname"))

    @patch("config.parser.frontend_config")
    def test__conf_celery(self, m_config):
        m_config.ssl_config.activate_ssl = True
        app = MagicMock()
        broker = MagicMock()
        module._conf_celery(app, broker)
        app.conf.update.assert_called_with(
            BROKER_USE_SSL={
               'ca_certs': m_config.ssl_config.ca_certs,
               'keyfile': m_config.ssl_config.keyfile,
               'certfile': m_config.ssl_config.certfile,
               'cert_reqs': module.ssl.CERT_REQUIRED
            }
        )

    @patch("config.parser.after_setup_task_logger")
    @patch("config.parser.after_setup_logger")
    @patch("config.parser.frontend_config")
    def test_configure_syslog(self, m_config, m_after_setup_logger,
                              m_after_setup_task_logger):
        app = MagicMock()
        m_config.log.syslog = True
        module.configure_syslog(app)
        app.conf.update.assert_called_with(CELERYD_LOG_COLOR=False)
        m_after_setup_logger.connect.assert_called_once_with(module.setup_log)
        m_after_setup_task_logger.connect.\
            assert_called_once_with(module.setup_log)

    def test_get_sample_storage_path(self):
        path = module.get_samples_storage_path()
        self.assertEqual(path, "/var/irma/samples")

    def test_setup_debug_logger(self):
        log = MagicMock()
        module.setup_debug_logger(log)
        log.setLevel.assert_called_once_with(module.logging.DEBUG)

    @patch("config.parser.frontend_config")
    def test_get_ftp_class_sftp(self, m_config):
        m_config.ftp_brain.auth = "password"
        m_config.ftp.protocol = "sftp"
        self.assertEqual(module.get_ftp_class(), module.IrmaSFTP)

    @patch("config.parser.os")
    @patch("config.parser.frontend_config")
    def test_get_ftp_class_sftp_error(self, m_config, m_os):
        m_config.ftp.protocol = "sftp"
        m_config.ftp_brain.auth = "key"
        m_os.path.isfile.return_value = False
        with self.assertRaises(module.IrmaConfigurationError):
            module.get_ftp_class()

    @patch("config.parser.frontend_config")
    def test_get_ftp_class_sftpv2(self, m_config):
        m_config.ftp_brain.auth = "password"
        m_config.ftp.protocol = "sftpv2"
        self.assertEqual(module.get_ftp_class(), module.IrmaSFTPv2)

    @patch("config.parser.frontend_config")
    def test_get_ftp_class_sftpv2_error(self, m_config):
        m_config.ftp.protocol = "sftpv2"
        m_config.ftp_brain.auth = "key"
        with self.assertRaises(module.IrmaConfigurationError):
            module.get_ftp_class()

    @patch("config.parser.frontend_config")
    def test_get_ftp_class_ftps(self, m_config):
        m_config.ftp.protocol = "ftps"
        self.assertEqual(module.get_ftp_class(), module.IrmaFTPS)
