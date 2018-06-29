#
# Copyright (c) 2013-2018 Quarkslab.
# This file is part of IRMA project.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License in the top-level directory
# of this distribution and at:
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# No part of the project, including this file, may be copied,
# modified, propagated, or distributed except according to the
# terms contained in the LICENSE file.

import logging
import hashlib
import unittest
import os
import random
from irma.common.utils.hash import md5sum, sha1sum, sha224sum, sha256sum, \
    sha384sum, sha512sum
from tempfile import TemporaryFile


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
        self.fobj = TemporaryFile()
        self.fobj.write(self.data)

    def tearDown(self):
        # do the teardown
        self.fobj.close()


class TestHashsum(HashTestCase):

    def test_hashsum_md5(self):
        hash1 = md5sum(self.fobj)
        hash2 = hashlib.md5(self.data).hexdigest()
        self.assertEqual(hash1, hash2)

    def test_hashsum_sha1(self):
        hash1 = sha1sum(self.fobj)
        hash2 = hashlib.sha1(self.data).hexdigest()
        self.assertEqual(hash1, hash2)

    def test_hashsum_sha224(self):
        hash1 = sha224sum(self.fobj)
        hash2 = hashlib.sha224(self.data).hexdigest()
        self.assertEqual(hash1, hash2)

    def test_hashsum_sha256(self):
        hash1 = sha256sum(self.fobj)
        hash2 = hashlib.sha256(self.data).hexdigest()
        self.assertEqual(hash1, hash2)

    def test_hashsum_sha384(self):
        hash1 = sha384sum(self.fobj)
        hash2 = hashlib.sha384(self.data).hexdigest()
        self.assertEqual(hash1, hash2)

    def test_hashsum_sha512(self):
        hash1 = sha512sum(self.fobj)
        hash2 = hashlib.sha512(self.data).hexdigest()
        self.assertEqual(hash1, hash2)


if __name__ == '__main__':
    enable_logging()
    unittest.main()
