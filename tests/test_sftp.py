#
# Copyright (c) 2013-2014 QuarksLab.
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
import os
from irma.ftp.sftp import IrmaSFTP
from tests.test_ftps import FTPSTestCase


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

class SFTPTestCase(FTPSTestCase):
    # Test config
    test_ftp_host = "irma.test"
    test_ftp_port = 2222
    test_ftp_user = "testuser"
    test_ftp_passwd = "testpwd"
    # needed if not chrooted in user home
    test_ftp_vuser = None
    test_ftp_uploadpath = None

    def setUp(self):
        # check database is ready for test
        self.ftp = IrmaSFTP
        self.ftp_connect()
        self.flush_all()
        self.cwd = os.path.dirname(os.path.realpath(__file__))

    def tearDown(self):
        # do the teardown
        self.flush_all()

if __name__ == '__main__':
    enable_logging()
    unittest.main()
