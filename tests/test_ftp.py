import logging
import hashlib
import unittest
import xmlrunner
import tempfile
import os
from irma.ftp.handler import FtpTls
from irma.common.exceptions import IrmaFtpError


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
class FtpTestCase(unittest.TestCase):
    # Test config
    test_ftp_host = "localhost"
    test_ftp_port = 21
    test_ftp_user = "testuser"
    test_ftp_passwd = "testpasswd"

    def setUp(self):
        # check database is ready for test
        self.ftp_running()
        self.flush_all()
        self.cwd = os.path.dirname(os.path.realpath(__file__))

    def tearDown(self):
        # do the teardown
        self.flush_all()

    def flush_all(self):
        # check that ftp server is empty before running tests
        try:
            ftps = FtpTls(self.test_ftp_host,
                          self.test_ftp_port,
                          self.test_ftp_user,
                          self.test_ftp_passwd)
            ftps.deletepath("/")
        except IrmaFtpError as e:
            print "Testftp Error: {0}".format(e)
            self.skipTest(FtpTestCase)

    def ftp_running(self):
        # check that ftp is up before running tests
        try:
            FtpTls(self.test_ftp_host,
                   self.test_ftp_port,
                   self.test_ftp_user,
                   self.test_ftp_passwd)
        except IrmaFtpError as e:
            print "Testftp Error: {0}".format(e)
            self.skipTest(FtpTestCase)


class TestFtpHandler(FtpTestCase):

    def test_ftp_upload_file(self):
        ftps = FtpTls(self.test_ftp_host,
                      self.test_ftp_port,
                      self.test_ftp_user,
                      self.test_ftp_passwd)
        filename = os.path.join(self.cwd, "test.ini")
        hashname = ftps.upload_file("/", filename)
        self.assertEqual(len(ftps.list("/")), 1)
        self.assertEqual(hashname,
                         hashlib.sha256(open(filename).read()).hexdigest())

    def test_ftp_upload_data(self):
        ftps = FtpTls(self.test_ftp_host,
                      self.test_ftp_port,
                      self.test_ftp_user,
                      self.test_ftp_passwd)
        filename = os.path.join(self.cwd, "test.ini")
        ftps.upload_file("/", filename)
        with open(filename, 'rb') as f:
            hashname = ftps.upload_data("/", f.read())
        self.assertEqual(len(ftps.list("/")), 1)
        self.assertEqual(hashname,
                         hashlib.sha256(open(filename).read()).hexdigest())

    def test_ftp_create_dir(self):
        ftps = FtpTls(self.test_ftp_host,
                      self.test_ftp_port,
                      self.test_ftp_user,
                      self.test_ftp_passwd)
        ftps.mkdir("test1")
        self.assertEqual(len(ftps.list("/")), 1)

    def test_ftp_create_subdir(self):
        ftps = FtpTls(self.test_ftp_host,
                      self.test_ftp_port,
                      self.test_ftp_user,
                      self.test_ftp_passwd)
        ftps.mkdir("/test1")
        ftps.mkdir("/test1/test2")
        ftps.mkdir("/test1/test2/test3")
        self.assertEqual(len(ftps.list("/")), 1)
        self.assertEqual(len(ftps.list("/test1")), 1)
        self.assertEqual(len(ftps.list("/test1/test2")), 1)
        self.assertEqual(len(ftps.list("/test1/test2/test3")), 0)

    def test_ftp_upload_in_subdir(self):
        ftps = FtpTls(self.test_ftp_host,
                      self.test_ftp_port,
                      self.test_ftp_user,
                      self.test_ftp_passwd)
        ftps.mkdir("/test1")
        ftps.mkdir("/test1/test2")
        ftps.mkdir("/test1/test2/test3")
        filename = os.path.join(self.cwd, "test.ini")
        hashname = ftps.upload_file("/test1/test2/test3", filename)
        self.assertEqual(len(ftps.list("/test1/test2/test3")), 1)
        self.assertEqual(hashname,
                         hashlib.sha256(open(filename).read()).hexdigest())

    def test_ftp_remove_not_existing_file(self):
        ftps = FtpTls(self.test_ftp_host,
                      self.test_ftp_port,
                      self.test_ftp_user,
                      self.test_ftp_passwd)
        with self.assertRaises(IrmaFtpError):
            ftps.delete(".", "lkzndlkaznd")

    def test_ftp_remove_not_existing_dir(self):
        ftps = FtpTls(self.test_ftp_host,
                      self.test_ftp_port,
                      self.test_ftp_user,
                      self.test_ftp_passwd)
        with self.assertRaises(IrmaFtpError):
            ftps.deletepath("/test1", deleteParent=True)

    def test_ftp_modify_file_hash(self):
        ftps = FtpTls(self.test_ftp_host,
                      self.test_ftp_port,
                      self.test_ftp_user,
                      self.test_ftp_passwd)
        filename = os.path.join(self.cwd, "test.ini")
        hashname = ftps.upload_file("/", filename)
        altered_name = "0000" + hashname[4:]
        ftps._conn.rename(hashname, altered_name)
        self.assertEqual(len(hashname), len(altered_name))
        _, tmpname = tempfile.mkstemp(prefix="test_ftp")
        with self.assertRaises(IrmaFtpError):
            ftps.download("/", altered_name, tmpname)
        os.unlink(tmpname)

    def test_ftp_download(self):
        ftps = FtpTls(self.test_ftp_host,
                      self.test_ftp_port,
                      self.test_ftp_user,
                      self.test_ftp_passwd)
        data = "TEST TEST TEST TEST"
        hashname = ftps.upload_data(".", data)
        _, tmpname = tempfile.mkstemp(prefix="test_ftp")
        ftps.download(".", hashname, tmpname)
        data2 = open(tmpname).read()
        os.unlink(tmpname)
        self.assertEqual(data, data2)

    def test_ftp_double_connect(self):
        FtpTls(self.test_ftp_host,
               self.test_ftp_port,
               self.test_ftp_user,
               self.test_ftp_passwd)
        FtpTls(self.test_ftp_host,
               self.test_ftp_port,
               self.test_ftp_user,
               self.test_ftp_passwd)
        # TODO when singleton will be done
        # self.assertEquals(ftp1, ftp2)

    def test_ftp_wrong_connect(self):
        with self.assertRaises(IrmaFtpError):
            FtpTls(self.test_ftp_host,
                   45000,
                   self.test_ftp_user,
                   self.test_ftp_passwd)

if __name__ == '__main__':
    enable_logging()
    xmlr = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=xmlr)
