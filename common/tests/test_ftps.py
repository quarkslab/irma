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
from irma.common.ftp.ftps import IrmaFTPS
from irma.common.base.exceptions import IrmaFtpError
from tempfile import TemporaryFile, mkstemp


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
class FTPSTestCase(unittest.TestCase):
    # Test config
    test_ftp_host = "irma.test"
    test_ftp_port = 21
    test_ftp_auth = "password"
    test_ftp_key = None
    test_ftp_user = "testuser"
    test_ftp_passwd = "testpwd"
    test_ftp_vuser = None
    test_ftp_uploadpath = None

    def setUp(self):
        # check database is ready for test
        self.ftp = IrmaFTPS
        self.ftp_connect()
        self.flush_all()
        self.cwd = os.path.dirname(os.path.realpath(__file__))

    def tearDown(self):
        # do the teardown
        self.flush_all()

    def flush_all(self):
        # check that ftp server is empty before running tests
        try:
            ftp = self.ftp_connect()
            ftp.deletepath("/")
        except IrmaFtpError as e:
            print("Testftp Error: {0}".format(e))
            self.skipTest(FTPSTestCase)

    def ftp_connect(self, host=None, port=None,
                    auth=None, key=None,
                    user=None, passwd=None,
                    vuser=None, upload_path=None):
        kwargs = {}
        if host is None:
            host = self.test_ftp_host
        if port is None:
            port = self.test_ftp_port
        if auth is None:
            auth = self.test_ftp_auth
        if key is None:
            key = self.test_ftp_key
        if user is None:
            user = self.test_ftp_user
        if passwd is None:
            passwd = self.test_ftp_passwd
        if vuser is not None:
            kwargs['vuser'] = self.test_ftp_vuser,
        if upload_path is not None:
            kwargs['upload_path'] = self.test_ftp_uploadpath
        # check that ftp is up before running tests
        try:
            return self.ftp(host,
                            port,
                            auth,
                            key,
                            user,
                            passwd,
                            **kwargs)
        except IrmaFtpError as e:
            print("Testftp Error: {0}".format(e))
            self.skipTest(FTPSTestCase)

    def test_ftp_upload_file(self):
        ftp = self.ftp_connect()
        filename = os.path.join(self.cwd, "test.ini")
        hashname = ftp.upload_file("/", filename)
        self.assertEqual(len(ftp.list("/")), 1)
        self.assertEqual(hashname,
                         hashlib.sha256(open(filename).read()).hexdigest())

    def test_ftp_upload_fobj(self):
        ftp = self.ftp_connect()
        t = TemporaryFile()
        data = "TEST TEST TEST TEST"
        t.write(data)
        hashname = ftp.upload_fobj("/", t)
        self.assertEqual(len(ftp.list("/")), 1)
        self.assertEqual(hashname,
                         hashlib.sha256(data).hexdigest())
        t.close()

    def test_ftp_create_dir(self):
        ftp = self.ftp_connect()
        ftp.mkdir("test1")
        self.assertEqual(len(ftp.list("/")), 1)

    def test_ftp_create_subdir(self):
        ftp = self.ftp_connect()
        ftp.mkdir("/test1")
        ftp.mkdir("/test1/test2")
        ftp.mkdir("/test1/test2/test3")
        self.assertEqual(len(ftp.list("/")), 1)
        self.assertEqual(len(ftp.list("/test1")), 1)
        self.assertEqual(len(ftp.list("/test1/test2")), 1)
        self.assertEqual(len(ftp.list("/test1/test2/test3")), 0)

    def test_ftp_upload_in_subdir(self):
        ftp = self.ftp_connect()
        ftp.mkdir("/test1")
        ftp.mkdir("/test1/test2")
        ftp.mkdir("/test1/test2/test3")
        filename = os.path.join(self.cwd, "test.ini")
        hashname = ftp.upload_file("/test1/test2/test3", filename)
        self.assertEqual(len(ftp.list("/test1/test2/test3")), 1)
        self.assertEqual(hashname,
                         hashlib.sha256(open(filename).read()).hexdigest())

    def test_ftp_remove_not_existing_file(self):
        ftp = self.ftp_connect()
        with self.assertRaises(IrmaFtpError):
            ftp.delete(".", "lkzndlkaznd")

    def test_ftp_remove_not_existing_dir(self):
        ftp = self.ftp_connect()
        with self.assertRaises(IrmaFtpError):
            ftp.deletepath("/test1", deleteParent=True)

    def test_ftp_modify_file_hash(self):
        ftp = self.ftp_connect()
        filename = os.path.join(self.cwd, "test.ini")
        hashname = ftp.upload_file("/", filename)
        altered_name = "0000" + hashname[4:]
        ftp.rename(hashname, altered_name)
        self.assertEqual(len(hashname), len(altered_name))
        t = TemporaryFile()
        with self.assertRaises(IrmaFtpError):
            ftp.download_file("/", altered_name, t)
        t.close()

    def test_ftp_download_file(self):
        ftp = self.ftp_connect()
        t = TemporaryFile()
        data = "TEST TEST TEST TEST"
        t.write(data)
        hashname = ftp.upload_fobj("/", t)
        _, tmpname = mkstemp(prefix="test_ftp")
        ftp.download_file(".", hashname, tmpname)
        data2 = open(tmpname).read()
        os.unlink(tmpname)
        self.assertEqual(data, data2)
        t.close()

    def test_ftp_download_fobj(self):
        ftp = self.ftp_connect()
        t1, t2 = TemporaryFile(), TemporaryFile()
        data = "TEST TEST TEST TEST"
        t1.write(data)
        hashname = ftp.upload_fobj(".", t1)
        ftp.download_fobj(".", hashname, t2)
        self.assertEqual(t2.read(), data)
        t1.close()
        t2.close()

    def test_ftp_already_connected(self):
        ftp = self.ftp(self.test_ftp_host,
                       self.test_ftp_port,
                       self.test_ftp_auth,
                       self.test_ftp_key,
                       self.test_ftp_user,
                       self.test_ftp_passwd)
        old_conn = ftp._conn
        ftp._connect()
        new_conn = ftp._conn
        # TODO when singleton will be done
        self.assertEqual(old_conn, new_conn)

    def test_ftp_double_connect(self):
        self.ftp(self.test_ftp_host,
                 self.test_ftp_port,
                 self.test_ftp_auth,
                 self.test_ftp_key,
                 self.test_ftp_user,
                 self.test_ftp_passwd)
        self.ftp(self.test_ftp_host,
                 self.test_ftp_port,
                 self.test_ftp_auth,
                 self.test_ftp_key,
                 self.test_ftp_user,
                 self.test_ftp_passwd)
        # TODO when singleton will be done
        # self.assertEquals(ftp1, ftp2)

    def test_ftp_wrong_port(self):
        with self.assertRaises(IrmaFtpError):
            self.ftp(self.test_ftp_host,
                     45000,
                     self.test_ftp_auth,
                     self.test_ftp_key,
                     self.test_ftp_user,
                     self.test_ftp_passwd)

    def test_ftp_wrong_user(self):
        with self.assertRaises(IrmaFtpError):
            self.ftp(self.test_ftp_host,
                     self.test_ftp_port,
                     self.test_ftp_auth,
                     self.test_ftp_key,
                     "random_foo",
                     self.test_ftp_passwd)

    def test_ftp_wrong_passwd(self):
        with self.assertRaises(IrmaFtpError):
            self.ftp(self.test_ftp_host,
                     self.test_ftp_port,
                     self.test_ftp_auth,
                     self.test_ftp_key,
                     self.test_ftp_user,
                     "random_bar")


if __name__ == '__main__':
    enable_logging()
    unittest.main()
