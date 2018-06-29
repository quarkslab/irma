import hashlib
from unittest import TestCase

from mock import MagicMock

import api.common.utils as module
from irma.common.utils.utils import UUID
from irma.common.base.exceptions import IrmaValueError, IrmaFileSystemError


class TestModuleUtils(TestCase):

    def setUp(self):
        self.old_config = module.config
        self.old_os = module.os
        module.config = MagicMock()
        module.os = MagicMock()

    def tearDown(self):
        module.config = self.old_config
        module.os = self.old_os

    def test_build_sha256_path_ok(self):
        sha = "1234567890"
        result = module.build_sha256_path(sha)
        self.assertTrue(module.config.get_samples_storage_path.called)
        self.assertEqual(module.os.path.join.call_count, 4)
        self.assertEqual(module.os.path.exists.call_count, 1)
        self.assertEqual(module.os.path.join.call_args,
                         ((module.os.path.join(), sha),))
        self.assertFalse(module.os.makedirs.called)
        self.assertEqual(result, module.os.path.join())

    def test_build_sha256_path_ok_and_path_not_exists(self):
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

    def test_build_sha256_path_raises_IrmaValueError(self):
        sha = str()
        with self.assertRaises(IrmaValueError) as context:
            module.build_sha256_path(sha)
        self.assertEqual(str(context.exception),
                         "too much prefix for file storage")
        self.assertTrue(module.config.get_samples_storage_path.called)
        self.assertFalse(module.os.path.join.called)
        self.assertFalse(module.os.path.exists.called)
        self.assertFalse(module.os.makedirs.called)

    def test_build_sha256_path_raises_IrmaFileSystemError(self):
        sha = "1234567890"
        module.os.path.isdir.return_value = False
        with self.assertRaises(IrmaFileSystemError) as context:
            module.build_sha256_path(sha)
        self.assertEqual(str(context.exception),
                         "storage path is not a directory")
        self.assertTrue(module.config.get_samples_storage_path.called)
        self.assertEqual(module.os.path.join.call_count, 3)
        self.assertEqual(module.os.path.exists.call_count, 1)
        self.assertFalse(module.os.makedirs.called)

    def test_validate_id(self):
        uuid = UUID.generate()
        self.assertIsNone(module.validate_id(uuid))

    def test_validate_id_raises(self):
        with self.assertRaises(ValueError) as context:
            module.validate_id("whatever")
        self.assertEqual(str(context.exception), "Malformed id")

    def test_validate_sha256(self):
        h = hashlib.sha256()
        h.update("whatever".encode("utf-8"))
        self.assertIsNone(module.validate_sha256(h.hexdigest()))

    def test_validate_sha256_raises(self):
        with self.assertRaises(ValueError) as context:
            module.validate_sha256("whatever")
        self.assertEqual(str(context.exception), "Malformed sha256")

    def test_validate_sha1(self):
        h = hashlib.sha1()
        h.update("whatever".encode("utf-8"))
        self.assertIsNone(module.validate_sha1(h.hexdigest()))

    def test_validate_sha1_raises(self):
        with self.assertRaises(ValueError) as context:
            module.validate_sha1("whatever")
        self.assertEqual(str(context.exception), "Malformed sha1")

    def test_validate_md5(self):
        h = hashlib.md5()
        h.update("whatever".encode("utf-8"))
        self.assertIsNone(module.validate_md5(h.hexdigest()))

    def test_validate_md5_raises(self):
        with self.assertRaises(ValueError) as context:
            module.validate_md5("whatever")
        self.assertEqual(str(context.exception), "Malformed md5")

    def test_guess_hash_type_md5(self):
        h = hashlib.md5()
        h.update("whatever".encode("utf-8"))
        val = h.hexdigest()
        self.assertEqual(module.guess_hash_type(val), "md5")

    def test_guess_hash_type_sha1(self):
        h = hashlib.sha1()
        h.update("whatever".encode("utf-8"))
        val = h.hexdigest()
        self.assertEqual(module.guess_hash_type(val), "sha1")

    def test_guess_hash_type_sha256(self):
        h = hashlib.sha256()
        h.update("whatever".encode("utf-8"))
        val = h.hexdigest()
        self.assertEqual(module.guess_hash_type(val), "sha256")

    def test_guess_hash_type_wrong_length(self):
        val = "whatever"
        self.assertIsNone(module.guess_hash_type(val))

    def test_guess_hash_type_wrong_hash(self):
        val = "w"*32
        self.assertIsNone(module.guess_hash_type(val))
