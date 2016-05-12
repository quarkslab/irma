from unittest import TestCase
from mock import MagicMock, patch

import frontend.controllers.scanctrl as module
from lib.irma.common.utils import IrmaScanStatus
from tempfile import TemporaryFile


class TestModuleScanctrl(TestCase):

    def setUp(self):
        self.old_File = module.File
        self.old_build_sha256_path = module.build_sha256_path
        self.File = MagicMock()
        self.build_sha256_path = MagicMock()
        module.File = self.File
        module.build_sha256_path = self.build_sha256_path

    def tearDown(self):
        module.File = self.old_File
        module.build_sha256_path = self.old_build_sha256_path
        del self.File
        del self.build_sha256_path

    def test001_add_files(self):
        fobj = TemporaryFile()
        filename = "n_test"
        scan, session = MagicMock(), MagicMock()
        function = "frontend.controllers.scanctrl.IrmaScanStatus.filter_status"
        with patch(function) as mock:
            module.add_files(scan, {filename: fobj}, session)
        self.assertTrue(mock.called)
        self.assertEqual(mock.call_args,
                         ((scan.status, IrmaScanStatus.empty,
                           IrmaScanStatus.ready),))
        self.assertTrue(self.File.load_from_sha256.called)
        self.assertTrue(self.build_sha256_path.called)
        fobj.close()
