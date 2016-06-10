from unittest import TestCase
from mock import patch, MagicMock

import frontend.controllers.ftpctrl as module
from lib.irma.common.exceptions import IrmaFtpError


class TestModuleFtpctrltasks(TestCase):

    @patch("frontend.controllers.ftpctrl.os.path")
    @patch('frontend.controllers.ftpctrl.config.IrmaSFTP')
    def test001_upload_scan(self, m_IrmaSFTP, m_ospath):
        scanid = "scanid1"
        filename = "file1"
        m_ftp = MagicMock()
        m_ftp.upload_file.return_value = filename
        m_IrmaSFTP().__enter__.return_value = m_ftp
        m_ospath.isfile.return_value = True
        m_ospath.basename.return_value = filename
        module.upload_scan(scanid, [filename])
        m_ospath.isfile.assert_called_once_with(filename)
        m_ftp.upload_file.assert_called_once_with(scanid, filename)

    @patch("frontend.controllers.ftpctrl.os.path")
    @patch('frontend.controllers.ftpctrl.config.IrmaSFTP')
    def test002_upload_scan_not_a_file(self, m_IrmaSFTP, m_ospath):
        scanid = "scanid2"
        filename = "file2"
        m_ospath.isfile.return_value = False
        with self.assertRaises(IrmaFtpError) as context:
            module.upload_scan(scanid, [filename])
        self.assertEqual(str(context.exception), "Ftp upload Error")

    @patch("frontend.controllers.ftpctrl.os.path")
    @patch('frontend.controllers.ftpctrl.config.IrmaSFTP')
    def test003_upload_scan_wrong_hash(self, m_IrmaSFTP, m_ospath):
        scanid = "scanid3"
        filename = "file3"
        m_ftp = MagicMock()
        m_ftp.upload_file.return_value = "whatever"
        m_IrmaSFTP().__enter__.return_value = m_ftp
        m_ospath.basename.return_value = filename
        m_ospath.isfile.return_value = True
        with self.assertRaises(IrmaFtpError) as context:
            module.upload_scan(scanid, [filename])
        self.assertEqual(str(context.exception), "Ftp upload Error")

    @patch("frontend.controllers.ftpctrl.TemporaryFile")
    @patch('frontend.controllers.ftpctrl.config.IrmaSFTP')
    def test004_download_data(self, m_IrmaSFTP, m_TemporaryFile):
        scanid = "scanid4"
        filename = "file4"
        m_ftp = MagicMock()
        m_fobj = MagicMock()
        m_TemporaryFile.return_value = m_fobj
        m_IrmaSFTP().__enter__.return_value = m_ftp
        module.download_file_data(scanid, filename)
        m_ftp.download_fobj.assert_called_once_with(scanid, filename, m_fobj)

    @patch("frontend.controllers.ftpctrl.TemporaryFile")
    @patch('frontend.controllers.ftpctrl.config.IrmaSFTP')
    def test005_download_data_raises(self, m_IrmaSFTP, m_TemporaryFile):
        scanid = "scanid5"
        filename = "file5"
        m_ftp = MagicMock()
        m_fobj = MagicMock()
        m_TemporaryFile.return_value = m_fobj
        m_IrmaSFTP().__enter__.return_value = m_ftp
        m_ftp.download_fobj.side_effect = Exception()
        with self.assertRaises(IrmaFtpError) as context:
            module.download_file_data(scanid, filename)
        self.assertEqual(str(context.exception), "Ftp download Error")
