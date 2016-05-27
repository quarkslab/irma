from unittest import TestCase
from mock import patch

import frontend.controllers.ftpctrl as module
from lib.irma.common.exceptions import IrmaFtpError


class TestModuleFtpctrltasks(TestCase):
    def setUp(self):
        patcher_ftp = patch('frontend.controllers.ftpctrl.config.IrmaSFTP')
        patcher_path = patch("frontend.controllers.ftpctrl.os.path")
        self.mftp = patcher_ftp.start()
        self.mpath = patcher_path.start()
        self.addCleanup(patcher_ftp.stop)
        self.addCleanup(patcher_path.stop)

    def tearDown(self):
        self.mftp.reset_mock()
        self.mpath.reset_mock()

    def test001_upload_scan(self):
        scanid = "scanid1"
        filename = "file1"
        handler = self.mftp.return_value.__enter__.return_value
        handler.upload_file.return_value = filename
        self.mpath.isfile.return_value = True
        self.mpath.basename.return_value = filename
        module.upload_scan(scanid, [filename])
        self.mpath.isfile.assert_called_once_with(filename)
        self.assertTrue(self.mftp.called)

    def test002_upload_scan_not_a_file(self):
        scanid = "scanid2"
        filename = "file2"
        self.mpath.isfile.return_value = False
        with self.assertRaises(IrmaFtpError) as context:
            module.upload_scan(scanid, [filename])
        self.assertEqual(str(context.exception), "Ftp upload Error")
        self.mpath.isfile.assert_called_once_with(filename)
        self.assertTrue(self.mftp.called)

    def test003_upload_scan_wrong_hash(self):
        scanid = "scanid3"
        filename = "file3"
        handler = self.mftp.return_value.__enter__.return_value
        handler.upload_file.return_value = "whatever"
        self.mpath.isfile.return_value = True
        with self.assertRaises(IrmaFtpError) as context:
            module.upload_scan(scanid, [filename])
        self.assertEqual(str(context.exception), "Ftp upload Error")
        self.mpath.isfile.assert_called_once_with(filename)
        self.assertTrue(self.mftp.called)
    """
    def test004_download_data(self):
        scanid = "scanid4"
        filename = "file4"
        handler = self.mftp.return_value.__enter__.return_value
        handler.download_fobj.return_value = "whatever"
        data = module.download_file_data(scanid, filename)
        self.assertEqual(data, "whatever")
        self.assertTrue(self.mftp.called)

    def test005_download_data_raises(self):
        scanid = "scanid5"
        filename = "file5"
        self.mftp.side_effect = Exception("whatever")
        with self.assertRaises(IrmaFtpError) as context:
            module.download_file_data(scanid, filename)
        self.assertEqual(str(context.exception), "Ftp download Error")
    """
