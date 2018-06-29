from unittest import TestCase
from mock import patch, MagicMock, call
import probe.controllers.ftpctrl as module
from irma.common.base.exceptions import IrmaFtpError


class TestFtpctrl(TestCase):

    @patch("probe.controllers.ftpctrl.os.path.isdir")
    @patch('probe.controllers.ftpctrl.config.IrmaSFTPv2')
    def test_upload_files(self, m_IrmaSFTPv2, m_isdir):
        parent_filename = "parent_file"
        filelist = ["file1", "file2"]
        m_ftp = MagicMock()
        m_IrmaSFTPv2().__enter__.return_value = m_ftp
        m_isdir.return_value = False
        module.upload_files("frontend", "path", filelist, parent_filename)
        m_isdir.assert_has_calls([call('path/file1'),
                                  call('path/file2')])
        m_ftp.upload_file.assert_has_calls([call('parent_file_0',
                                                 'path/file1'),
                                            call('parent_file_1',
                                                 'path/file2')])

    @patch("probe.controllers.ftpctrl.os.path.isdir")
    @patch('probe.controllers.ftpctrl.config.IrmaSFTPv2')
    def test_upload_files_not_a_file(self, m_IrmaSFTPv2, m_isdir):
        m_isdir.return_value = True
        m_ftp = MagicMock()
        m_IrmaSFTPv2().__enter__.return_value = m_ftp
        module.upload_files("frontend", "path", ["dir"], "parent_file")
        m_ftp.upload_file.assert_not_called()

    @patch('probe.controllers.ftpctrl.config.IrmaSFTPv2')
    def test_download_file(self, m_IrmaSFTPv2):
        filename = "file4"
        m_ftp = MagicMock()
        m_IrmaSFTPv2().__enter__.return_value = m_ftp
        module.download_file("frontend", "srcname", filename)
        m_ftp.download_file.assert_called_once_with(".", "srcname", filename)
