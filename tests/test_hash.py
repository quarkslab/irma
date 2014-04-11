import logging
import hashlib
import unittest
import tempfile
import os
import random
import common.hash as irma_hashlib


# =================
#  Logging options
# =================

def enable_logging(level=logging.INFO, handler=None, formatter=None):
    global log
    log = logging.getLogger()
    if formatter is None:
        formatter = logging.Formatter("%(asctime)s [%(name)s] " +
                                      "%(levelname)s: %(message)s")
    if handler is None:
        handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.setLevel(level)


# ============
#  Test Cases
# ============
class HashTestCase(unittest.TestCase):

    def setUp(self):
        # build up to 1Mb data buffer
        self.data = os.urandom(random.randrange(1024, 1024 * 1024))
        _, self.filename = tempfile.mkstemp(prefix="test_hash")
        with open(self.filename, "wb") as f:
            f.write(self.data)

    def tearDown(self):
        # do the teardown
        os.remove(self.filename)


class TestHashsum(HashTestCase):

    def test_hashsum_md5(self):
        hash1 = irma_hashlib.md5sum(self.filename)
        hash2 = hashlib.md5(self.data).hexdigest()
        self.assertEqual(hash1, hash2)

    def test_hashsum_sha1(self):
        hash1 = irma_hashlib.sha1sum(self.filename)
        hash2 = hashlib.sha1(self.data).hexdigest()
        self.assertEqual(hash1, hash2)

    def test_hashsum_sha224(self):
        hash1 = irma_hashlib.sha224sum(self.filename)
        hash2 = hashlib.sha224(self.data).hexdigest()
        self.assertEqual(hash1, hash2)

    def test_hashsum_sha256(self):
        hash1 = irma_hashlib.sha256sum(self.filename)
        hash2 = hashlib.sha256(self.data).hexdigest()
        self.assertEqual(hash1, hash2)

    def test_hashsum_sha384(self):
        hash1 = irma_hashlib.sha384sum(self.filename)
        hash2 = hashlib.sha384(self.data).hexdigest()
        self.assertEqual(hash1, hash2)

    def test_hashsum_sha512(self):
        hash1 = irma_hashlib.sha512sum(self.filename)
        hash2 = hashlib.sha512(self.data).hexdigest()
        self.assertEqual(hash1, hash2)


if __name__ == '__main__':
    enable_logging()
    unittest.main()
