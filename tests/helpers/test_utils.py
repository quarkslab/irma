from unittest import TestCase
from mock import MagicMock, patch

import frontend.helpers.utils as module
from lib.irma.common.exceptions import IrmaValueError, IrmaFileSystemError


class TestModuleUtils(TestCase):

    def setUp(self):
        self.old_config = module.config
        self.old_os = module.os
        module.config = MagicMock()
        module.os = MagicMock()

    def tearDown(self):
        module.config = self.old_config
        module.os = self.old_os

    def test001_build_sha256_path_ok(self):
        sha = "1234567890"
        result = module.build_sha256_path(sha)
        self.assertTrue(module.config.get_samples_storage_path.called)
        self.assertEqual(module.os.path.join.call_count, 4)
        self.assertEqual(module.os.path.exists.call_count, 1)
        self.assertEqual(module.os.path.join.call_args,
                         ((module.os.path.join(), sha),))
        self.assertFalse(module.os.makedirs.called)
        self.assertEqual(result, module.os.path.join())

    def test002_build_sha256_path_ok_and_path_not_exists(self):
        sha = "1234567890"
        module.os.path.exists.return_value = False
        result = module.build_sha256_path(sha)
        self.assertTrue(module.config.get_samples_storage_path.called)
        self.assertEqual(module.os.path.join.call_count, 4)
        self.assertEqual(module.os.makedirs.call_count, 1)
        self.assertEqual(module.os.path.exists.call_count, 1)
        self.assertEqual(module.os.path.join.call_args,
                         ((module.os.path.join(), sha),))
        self.assertEqual(result, module.os.path.join())

    def test003_build_sha256_path_raises_IrmaValueError(self):
        sha = str()
        with self.assertRaises(IrmaValueError) as context:
            module.build_sha256_path(sha)
        self.assertEqual(str(context.exception),
                         "too much prefix for file storage")
        self.assertTrue(module.config.get_samples_storage_path.called)
        self.assertFalse(module.os.path.join.called)
        self.assertFalse(module.os.path.exists.called)
        self.assertFalse(module.os.makedirs.called)

    def test004_build_sha256_path_raises_IrmaFileSystemError(self):
        sha = "1234567890"
        module.os.path.isdir.return_value = False
        with self.assertRaises(IrmaFileSystemError) as context:
            module.build_sha256_path(sha)
        self.assertEquals(str(context.exception),
                          "storage path is not a directory")
        self.assertTrue(module.config.get_samples_storage_path.called)
        self.assertEqual(module.os.path.join.call_count, 3)
        self.assertEqual(module.os.path.exists.call_count, 1)
        self.assertFalse(module.os.makedirs.called)

    def test005_write_sample_on_disk_ok(self):
        sha, data = "sha_test", "data_test"
        with patch("%s.build_sha256_path" % module.__name__,
                   create=True) as mock_build_path:
            with patch("%s.open" % module.__name__, create=True) as mock_open:
                result = module.write_sample_on_disk(sha, data)
        self.assertEqual(mock_build_path.call_count, 1)
        self.assertEqual(mock_build_path.call_args, ((sha,),))
        self.assertEqual(mock_open.call_count, 1)
        self.assertEqual(mock_open.call_args, ((mock_build_path(sha), "wb"),))
        self.assertEqual(mock_open().__enter__().write.call_count, 1)
        self.assertEqual(mock_open().__enter__().write.call_args, ((data,),))
        self.assertEqual(result, mock_build_path(sha))

    def test006_write_sample_on_disk_raises_IrmaFileSystemError(self):
        sha, data = "sha_test", "data_test"
        with patch("%s.build_sha256_path" % module.__name__,
                   create=True) as mock_build_path:
            with patch("%s.open" % module.__name__, create=True) as mock_open:
                mock_open().__enter__().write.side_effect = IOError()
                with self.assertRaises(IrmaFileSystemError) as context:
                    result = module.write_sample_on_disk(sha, data)
        expected = "Cannot add the sample {0} to the collection".format(sha)
        self.assertEqual(str(context.exception),
                         expected)
