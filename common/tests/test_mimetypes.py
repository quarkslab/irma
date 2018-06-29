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
import unittest
import tempfile
import os

import magic
from irma.common.utils.mimetypes import Magic


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
class MimetypesTestCase(unittest.TestCase):

    def create_pdf(self):
        return b"%PDF-1.2"

    def setUp(self):
        # build up to 1Mb data buffer
        self.data = self.create_pdf()
        _, self.filename = tempfile.mkstemp(prefix="test_magic")
        with open(self.filename, "wb") as f:
            f.write(self.data)
        try:
            self.cookie = magic.open(magic.MAGIC_NONE |
                                     magic.MAGIC_MIME |
                                     magic.MAGIC_MIME_ENCODING |
                                     magic.MAGIC_CONTINUE)
            self.cookie.load()
        except AttributeError:
            self.cookie = magic.Magic(mime=True,
                                      magic_file=None,
                                      mime_encoding=True,
                                      keep_going=True)
            self.cookie.file = self.cookie.from_file
            self.cookie.buffer = self.cookie.from_buffer

    def tearDown(self):
        # do the teardown
        os.remove(self.filename)


class TestMimetype(MimetypesTestCase):

    def test_from_buffer(self):
        mime1 = Magic.from_buffer(self.data,
                                  mime=True,
                                  mime_encoding=True,
                                  keep_going=True)
        mime2 = self.cookie.buffer(self.data)
        self.assertEqual(mime1, mime2)

    def test_from_file(self):
        mime1 = Magic.from_file(self.filename,
                                mime=True,
                                mime_encoding=True,
                                keep_going=True)
        mime2 = self.cookie.file(self.filename)
        self.assertEqual(mime1, mime2)


if __name__ == '__main__':
    enable_logging()
    unittest.main()
