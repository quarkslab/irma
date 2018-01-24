from unittest import TestCase

from mock import patch, MagicMock

import api.common.ftp as module
from lib.irma.common.exceptions import IrmaFtpError


class TestModuleFtpctrltasks(TestCase):

    @patch("api.common.ftp.os.path")
    @patch('api.common.ftp.config.IrmaSFTP')
    def test_upload_file(self, m_IrmaSFTP, m_ospath):
        upload_path = "path1"
        filename = "file1"
        m_ftp = MagicMock()
        m_IrmaSFTP().__enter__.return_value = m_ftp
        m_ospath.isfile.return_value = True
        m_ospath.basename.return_value = filename
        module.upload_file(upload_path, filename)
        m_ospath.isfile.assert_called_once_with(filename)
        m_ftp.upload_file.assert_called_once_with(upload_path, filename)

    @patch("api.common.ftp.os.path")
    @patch('api.common.ftp.config.IrmaSFTP')
    def test_upload_file_not_a_file(self, m_IrmaSFTP, m_ospath):
        upload_path = "path2"
        filename = "file2"
        m_ospath.isfile.return_value = False
        with self.assertRaises(IrmaFtpError) as context:
            module.upload_file(upload_path, filename)
        self.assertEqual(str(context.exception), "Ftp upload Error")

    @patch("api.common.ftp.TemporaryFile")
    @patch('api.common.ftp.config.IrmaSFTP')
    def test_download_data(self, m_IrmaSFTP, m_TemporaryFile):
        filename = "file4"
        m_ftp = MagicMock()
        m_fobj = MagicMock()
        m_TemporaryFile.return_value = m_fobj
        m_IrmaSFTP().__enter__.return_value = m_ftp
        module.download_file_data(filename)
        m_ftp.download_fobj.assert_called_once_with(".", filename, m_fobj)

    @patch("api.common.ftp.TemporaryFile")
    @patch('api.common.ftp.config.IrmaSFTP')
    def test_download_data_raises(self, m_IrmaSFTP, m_TemporaryFile):
        filename = "file5"
        m_ftp = MagicMock()
        m_fobj = MagicMock()
        m_TemporaryFile.return_value = m_fobj
        m_IrmaSFTP().__enter__.return_value = m_ftp
        m_ftp.download_fobj.side_effect = Exception()
        with self.assertRaises(IrmaFtpError) as context:
            module.download_file_data(filename)
        self.assertEqual(str(context.exception), "Ftp download Error")
