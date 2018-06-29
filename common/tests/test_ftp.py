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

import unittest
from mock import Mock, MagicMock, patch
from irma.common.ftp.ftp import FTPInterface, _tweaked_join
from irma.common.ftp.sftp import IrmaSFTP
from irma.common.ftp.sftpv2 import IrmaSFTPv2
from irma.common.ftp.ftps import IrmaFTPS, IrmaConfigurationError, FTP_TLS_Data
import os.path


class TestFTP(unittest.TestCase):

    ftp_cls = FTPInterface

    def setUp(self):
        if self.ftp_cls == FTPInterface:
            self.skipTest("Abstract class, cannot be instanciated")

        self.ftp = self.ftp_cls("host", "port", "password", "key_path", "user",
                                "passwd", dst_user="ruser",
                                upload_path="uploads", hash_check=False,
                                autoconnect=False)

    def tearDown(self):
        if hasattr(self, "ftp"):
            self.ftp._disconnect = lambda *_: None

    @patch("irma.common.ftp.ftp.FTPInterface.connect")
    def test_autoconnect(self, m_connect):
        self.ftp = self.ftp_cls("host", "port", "password", "key_path", "user",
                                "passwd", dst_user="ruser",
                                upload_path="uploads", hash_check=False,
                                autoconnect=True)
        m_connect.assert_called_once()

    def test__del__0(self):
        self.ftp.connected = Mock(return_value=False)
        m_disconnect = Mock()
        self.ftp.disconnect = m_disconnect

        del(self.ftp)

        m_disconnect.assert_not_called()

    def test__del__1(self):
        self.ftp.connected = Mock(return_value=True)
        m_disconnect = Mock()
        self.ftp.disconnect = m_disconnect

        del(self.ftp)

        m_disconnect.assert_called_once()

    def test__enter__0(self):
        self.ftp.disconnect = Mock()
        with self.ftp as ftp:
            self.assertIs(ftp, self.ftp)
        self.ftp.disconnect.assert_called_once()

    def test__enter__1(self):
        self.ftp._connect = Mock()
        self.ftp.disconnect = Mock()
        self.ftp.connected = Mock(return_value=False)

        with self.ftp.connect() as ftp:
            self.ftp.connected = Mock(return_value=True)
            self.assertIs(ftp, self.ftp)

        self.ftp.disconnect.assert_called_once()

    @patch("irma.common.ftp.ftp.log")
    def test_connect0(self, m_log):
        self.ftp.connected = Mock(return_value=True)
        self.ftp._connect = Mock()

        self.ftp.connect()

        self.ftp.connected.assert_called_once()
        self.ftp._connect.assert_not_called()
        m_log.warn.assert_called_once()

    @patch("irma.common.ftp.ftp.log")
    def test_connect1(self, m_log):
        self.ftp.connected = Mock(return_value=False)
        self.ftp._connect = Mock(side_effect=Exception)

        with self.assertRaises(self.ftp._Exception):
            self.ftp.connect()

        self.ftp.connected.assert_called_once()
        self.ftp._connect.assert_called_once()
        m_log.warn.assert_not_called()

    @patch("irma.common.ftp.ftp.log")
    def test_connect2(self, m_log):
        self.ftp.connected = Mock(return_value=False)
        self.ftp._connect = Mock()

        self.ftp.connect()

        self.ftp.connected.assert_called_once()
        self.ftp._connect.assert_called_once()
        m_log.warn.assert_not_called()

    @patch("irma.common.ftp.ftp.log")
    def test_disconnect0(self, m_log):
        self.ftp.connected = Mock(return_value=False)
        self.ftp._disconnect = Mock()

        self.ftp.disconnect()

        self.ftp.connected.assert_called_once()
        self.ftp._disconnect.assert_not_called()
        m_log.warn.assert_called_once()
        m_log.error.assert_not_called()

    @patch("irma.common.ftp.ftp.log")
    def test_disconnect1(self, m_log):
        self.ftp.connected = Mock(return_value=True)
        self.ftp._disconnect = Mock(side_effect=[Exception, None])

        with self.assertRaises(self.ftp._Exception):
            self.ftp.disconnect()

        self.ftp.connected.assert_called_once()
        self.ftp._disconnect.assert_any_call()
        self.ftp._disconnect.assert_any_call(force=True)
        self.assertEqual(self.ftp._disconnect.call_count, 2)
        m_log.warn.assert_not_called()
        m_log.error.assert_called_once()

    @patch("irma.common.ftp.ftp.log")
    def test_disconnect2(self, m_log):
        self.ftp.connected = Mock(return_value=True)
        self.ftp._disconnect = Mock()

        self.ftp.disconnect()

        self.ftp.connected.assert_called_once()
        self.ftp._disconnect.assert_called_once()
        m_log.warn.assert_not_called()
        m_log.error.assert_not_called()

    @patch("builtins.open", spec=open)
    def test_upload_file0(self, m_open):
        self.ftp.upload_fobj = Mock(return_value="/foo")

        result = self.ftp.upload_file("/bar", "/baz")
        m_open.assert_called_once_with("/baz", 'rb')
        self.assertEqual(result, "/foo")
        self.ftp.upload_fobj.assert_called_once()

    @patch("builtins.open", spec=open)
    def test_upload_file1(self, m_open):
        self.ftp.upload_fobj = Mock(side_effect=self.ftp._Exception)

        with self.assertRaises(self.ftp._Exception):
            self.ftp.upload_file("/bar", "/baz")
        m_open.assert_called_once_with("/baz", 'rb')
        self.ftp.upload_fobj.assert_called_once()

    @patch("builtins.open", spec=open)
    def test_upload_file2(self, m_open):
        self.ftp.upload_fobj = Mock()
        m_open.side_effect = FileNotFoundError()

        with self.assertRaises(FileNotFoundError):
            self.ftp.upload_file("/bar", "/baz")
        self.ftp.upload_fobj.assert_not_called()

    @patch("builtins.open", spec=open)
    def test_download_file0(self, m_open):
        self.ftp.download_fobj = Mock()

        self.ftp.download_file("/foo", "/bar", "/baz")
        m_open.assert_called_once_with("/baz", 'wb+')
        self.ftp.download_fobj.assert_called_once()

    @patch("builtins.open", spec=open)
    def test_download_file1(self, m_open):
        self.ftp.download_fobj = Mock(side_effect=self.ftp._Exception)

        with self.assertRaises(self.ftp._Exception):
            self.ftp.download_file("/foo", "/bar", "/baz")
        m_open.assert_called_once_with("/baz", 'wb+')
        self.ftp.download_fobj.assert_called_once()

    @patch("builtins.open", spec=open)
    def test_download_file2(self, m_open):
        self.ftp.download_fobj = Mock()
        m_open.side_effect = FileNotFoundError()

        with self.assertRaises(FileNotFoundError):
            self.ftp.download_file("/foo", "/bar", "/baz")
        self.ftp.download_fobj.assert_not_called()

    def test_upload_fobj0(self):
        self.ftp._upload = Mock(side_effect=Exception)

        with self.assertRaises(self.ftp._Exception):
            self.ftp.upload_fobj("path", "fobj")

        self.ftp._upload.assert_called_once()

    def test_upload_fobj1(self):
        self.ftp._upload = Mock()

        self.ftp.upload_fobj("foo", "fobj")

        self.ftp._upload.assert_called_once_with("ruser/uploads/foo", "fobj")

    def test_upload_fobj2(self):
        self.ftp._upload = Mock()
        self.ftp.hash_check = True
        self.ftp._hash = Mock(return_value="c63508a9")

        res = self.ftp.upload_fobj("foo", "fobj")

        self.ftp._upload.assert_called_once_with(
                "ruser/uploads/foo/c63508a9", "fobj")
        self.assertEqual(res, "c63508a9")

    def test_download_fobj0(self):
        self.ftp._download = Mock(side_effect=Exception)

        with self.assertRaises(self.ftp._Exception):
            self.ftp.download_fobj("path", "bar", "fobj")

        self.ftp._download.assert_called_once()

    def test_download_fobj1(self):
        self.ftp._download = Mock()

        self.ftp.download_fobj("foo", "bar", "fobj")

        self.ftp._download.assert_called_once_with(
                "ruser/uploads/foo/bar", "fobj")

    @patch("irma.common.ftp.ftp.FTPInterface._hash")
    def test_download_fobj2(self, m_hash):
        self.ftp._download = Mock()
        self.ftp.hash_check = True
        m_hash.return_value = "c63508a9"

        with self.assertRaises(self.ftp._Exception):
            self.ftp.download_fobj("foo", "bar", "fobj")

    @patch("irma.common.ftp.ftp.FTPInterface._hash")
    def test_download_fobj3(self, m_hash):
        self.ftp._download = Mock()
        self.ftp.hash_check = True
        m_hash.return_value = "c63508a9"

        self.ftp.download_fobj("foo", "c63508a9", "fobj")

        expected = "ruser/uploads/foo/c63508a9"
        self.ftp._download.assert_called_once_with(expected, "fobj")

    def test_list0(self):
        self.ftp._ls = Mock(side_effect=Exception)

        with self.assertRaises(self.ftp._Exception):
            self.ftp.list("foo")

    def test_list1(self):
        self.ftp._ls = Mock(return_value="sthg")

        res = self.ftp.list("foo")

        self.ftp._ls.assert_called_once_with("ruser/uploads/foo")
        self.assertEqual(res, "sthg")

    def test_is_file0(self):
        self.ftp._is_file = Mock(side_effect=Exception)

        with self.assertRaises(self.ftp._Exception):
            self.ftp.is_file("foo", "bar")

    def test_is_file1(self):
        self.ftp._is_file = Mock(return_value="sthg")

        res = self.ftp.is_file("foo", "bar")

        self.ftp._is_file.assert_called_once_with("ruser/uploads/foo/bar")
        self.assertEqual(res, "sthg")

    def test_delete0(self):
        self.ftp._rm = Mock(side_effect=Exception)

        with self.assertRaises(self.ftp._Exception):
            self.ftp.delete("foo", "bar")

    def test_delete1(self):
        self.ftp._rm = Mock()

        self.ftp.delete("foo", "bar")

        self.ftp._rm.assert_called_once_with("ruser/uploads/foo/bar")

    def test_mkdir0(self):
        self.ftp._mkdir = Mock(side_effect=Exception)

        with self.assertRaises(self.ftp._Exception):
            self.ftp.mkdir("foo")

    def test_mkdir1(self):
        self.ftp._mkdir = Mock()

        self.ftp.mkdir("foo")

        self.ftp._mkdir.assert_called_once_with("ruser/uploads/foo")

    def test_rename0(self):
        self.ftp._mv = Mock(side_effect=Exception)

        with self.assertRaises(self.ftp._Exception):
            self.ftp.rename("foo", "bar")

    def test_rename1(self):
        self.ftp._mv = Mock()

        self.ftp.rename("foo", "bar")

        self.ftp._mv.assert_called_once_with(
                "ruser/uploads/foo", "ruser/uploads/bar")

    def test_hash(self):
        f = Mock()
        f.read.side_effect = (b"something", b"", )
        result = self.ftp._hash(f)
        expected = "3fc9b689459d738f8c88a3a48aa9e335"\
                   "42016b7a4052e001aaa536fca74813cb"
        self.assertEqual(result, expected)

    def test_get_realpath0(self):
        self.ftp._upload_path = None
        self.ftp._dst_user = None
        result = self.ftp._get_realpath("foo")
        result = os.path.normpath(result)
        self.assertEqual(result, "foo")

    def test_get_realpath1(self):
        self.ftp._upload_path = None
        result = self.ftp._get_realpath("foo")
        result = os.path.normpath(result)
        self.assertEqual(result, "ruser/foo")

    def test_get_realpath2(self):
        result = self.ftp._get_realpath("foo")
        result = os.path.normpath(result)
        self.assertEqual(result, "ruser/uploads/foo")


class TestSFTP(TestFTP):
    ftp_cls = IrmaSFTP

    def setUp(self):
        super().setUp()
        self.ftp._conn = Mock()
        self.ftp._client = Mock()

    @patch("irma.common.ftp.sftp.SFTPClient")
    @patch("irma.common.ftp.sftp.Transport")
    @patch("irma.common.ftp.sftp.RSAKey")
    def test_connect_o0(self, m_RSAKey, m_Transport, m_SFTPClient):
        conn = Mock()
        m_Transport.return_value = conn
        self.ftp._auth = "key"

        self.ftp._connect()

        m_RSAKey.from_private_key_file.assert_called_once_with("key_path")
        self.assertIs(self.ftp._conn, conn)
        conn.connect.assert_called_once_with(
                username="user", pkey=m_RSAKey.from_private_key_file())

    @patch("irma.common.ftp.sftp.SFTPClient")
    @patch("irma.common.ftp.sftp.Transport")
    @patch("irma.common.ftp.sftp.RSAKey")
    def test_connect_o1(self, m_RSAKey, m_Transport, m_SFTPClient):
        conn = Mock()
        m_Transport.return_value = conn
        self.ftp._auth = "password"

        self.ftp._connect()

        m_RSAKey.from_private_key_file.assert_not_called()
        self.assertIs(self.ftp._conn, conn)
        conn.connect.assert_called_once_with(
                username="user", password="passwd")

    def test_disconnect_o0(self):
        self.ftp._disconnect(force=True)

        self.assertFalse(self.ftp.connected())

    def test_disconnect_o1(self):
        conn = self.ftp._conn

        self.ftp._disconnect()

        self.assertFalse(self.ftp.connected())
        conn.close.assert_called_once()

    def test_upload_o0(self):
        self.ftp._upload("foo", "fobj")

        self.ftp._client.putfo.assert_called_once_with("fobj", "foo")

    def test_download_o0(self):
        self.ftp._download("foo", "fobj")

        self.ftp._client.getfo.assert_called_once_with("foo", "fobj")

    def test_ls_o0(self):
        self.ftp._client.listdir.return_value = "sthg"

        res = self.ftp._ls("foo")

        self.ftp._client.listdir.assert_called_once_with("foo")
        self.assertEqual(res, "sthg")

    def test_is_file_o0(self):
        self.ftp._is_dir = Mock(return_value=True)

        res = self.ftp._is_file("foo")

        self.ftp._is_dir.assert_called_once_with("foo")
        self.assertNotEqual(res, True)

    @patch("irma.common.ftp.sftp.stat")
    def test_is_dir_o0(self, m_stat):
        m_stat.S_ISDIR.return_value = False

        res = self.ftp._is_dir("foo")

        self.ftp._client.stat.assert_called_with("foo")
        self.assertFalse(res)

    def test_rm_o0(self):
        self.ftp._rm("foo")

        self.ftp._client.remove.assert_called_with("foo")

    def test_rmdir_o0(self):
        self.ftp._rmdir("foo")

        self.ftp._client.rmdir.assert_called_with("foo")

    def test_mkdir_o0(self):
        self.ftp._mkdir("foo")

        self.ftp._client.mkdir.assert_called_with("foo")

    def test_mv_o0(self):
        self.ftp._mv("foo", "bar")

        self.ftp._client.rename.assert_called_with("foo", "bar")


class TestSFTPv2(TestFTP):
    ftp_cls = IrmaSFTPv2

    def setUp(self):
        super().setUp()
        self.ftp._sess = Mock()
        self.ftp._client = Mock()

    @patch("irma.common.ftp.sftpv2.Session")
    @patch("irma.common.ftp.sftpv2.socket")
    def test_connect_o0(self, m_socket, m_Session):
        self.ftp._auth = "key"

        with self.assertRaises(self.ftp._Exception):
            self.ftp._connect()

        m_socket.socket().connect.assert_called_once_with(("host", "port"))
        m_Session().handshake.assert_called_once_with(m_socket.socket())

    @patch("irma.common.ftp.sftpv2.Session")
    @patch("irma.common.ftp.sftpv2.socket")
    def test_connect_o1(self, m_socket, m_Session):
        self.ftp._auth = "password"

        self.ftp._connect()

        m_socket.socket().connect.assert_called_once_with(("host", "port"))
        m_Session().handshake.assert_called_once_with(m_socket.socket())
        m_Session().userauth_password.assert_called_once_with("user", "passwd")
        m_Session().sftp_init.assert_called_once()

    def test_disconnect_o0(self):
        self.ftp._disconnect(force=True)

        self.assertFalse(self.ftp.connected())

    def test_disconnect_o1(self):
        sess = self.ftp._sess

        self.ftp._disconnect()

        self.assertFalse(self.ftp.connected())
        sess.disconnect.assert_called_once()

    def test_upload_o0(self):
        m_rfh = MagicMock()
        self.ftp._client.open.return_value = m_rfh
        fobj = Mock()
        fobj.read.side_effect = (b"bar", b"baz", b"")

        self.ftp._upload("foo", fobj)

        self.ftp._client.open.assert_called_once()
        m_rfh.__enter__().write.assert_any_call(b"bar")
        m_rfh.__enter__().write.assert_any_call(b"baz")

    def test_download_o0(self):
        m_rfh = MagicMock()
        m_rfh.__enter__().__iter__.return_value = iter(
                [(3, b"bar"), (3, b"baz"), (0, b"")])
        self.ftp._client.open.return_value = m_rfh
        fobj = Mock()

        self.ftp._download("foo", fobj)

        self.ftp._client.open.assert_called_once_with("foo", 0, 0)
        fobj.write.assert_any_call(b"bar")
        fobj.write.assert_any_call(b"baz")
        fobj.write.assert_any_call(b"")

    def test_ls_o0(self):
        m_rfh = MagicMock()
        m_rfh.__enter__().readdir.return_value = [
                ("whatever", b"bar"), ("again", b".baz"), ("toto", b".")]
        self.ftp._client.opendir = MagicMock(return_value=m_rfh)

        res = self.ftp._ls("foo")

        self.ftp._client.opendir.assert_called_once_with("foo")
        self.assertEqual(res, ["bar", ".baz"])

    def test_is_file_o0(self):
        self.ftp._is_dir = Mock(return_value=True)

        res = self.ftp._is_file("foo")

        self.ftp._is_dir.assert_called_once_with("foo")
        self.assertNotEqual(res, True)

    @patch("irma.common.ftp.sftpv2.stat")
    def test_is_dir_o0(self, m_stat):
        m_stat.S_ISDIR.return_value = False

        res = self.ftp._is_dir("foo")

        self.ftp._client.stat.assert_called_with("foo")
        self.assertFalse(res)

    def test_rm_o0(self):
        self.ftp._rm("foo")

        self.ftp._client.unlink.assert_called_with("foo")

    def test_rmdir_o0(self):
        self.ftp._rmdir("foo")

        self.ftp._client.rmdir.assert_called_with("foo")

    def test_mkdir_o0(self):
        self.ftp._mkdir("foo")

        self.ftp._client.mkdir.assert_called_with("foo", 0o700)

    def test_mv_o0(self):
        self.ftp._mv("foo", "bar")

        self.ftp._client.rename.assert_called_with("foo", "bar")


class TestFTPS(TestFTP):
    ftp_cls = IrmaFTPS

    def setUp(self):
        self.ftp = self.ftp_cls("host", 21, "password", "key_path", "user",
                                "passwd", dst_user="ruser",
                                upload_path="uploads", hash_check=False,
                                autoconnect=False)
        self.ftp._conn = Mock()

    @patch("irma.common.ftp.ftp.FTPInterface.connect")
    def test_autoconnect(self, m_connect):
        self.ftp = self.ftp_cls("host", 21, "password", "key_path", "user",
                                "passwd", dst_user="ruser",
                                upload_path="uploads", hash_check=False,
                                autoconnect=True)
        m_connect.assert_called_once()

    def test__init__0(self):
        with self.assertRaises(IrmaConfigurationError):
            self.ftp_cls("host", 21, "key", "key_path", "user", "passwd",
                         dst_user="ruser", upload_path="uploads",
                         hash_check=False, autoconnect=True)

    def test__init__1(self):
        with self.assertRaises(self.ftp._Exception):
            self.ftp_cls("host", 25, "password", "key_path", "user", "passwd",
                         dst_user="ruser", upload_path="uploads",
                         hash_check=False, autoconnect=True)

    @patch("irma.common.ftp.ftps.FTP_TLS_Data")
    def test_connect_o0(self, m_FTP_TLS_Data):
        conn = Mock()
        m_FTP_TLS_Data.return_value = conn

        self.ftp._connect()

        self.assertIs(self.ftp._conn, conn)
        conn.prot_p.assert_called_once()

    def test_disconnect_o0(self):
        self.ftp._disconnect(force=True)

        self.assertFalse(self.ftp.connected())

    def test_disconnect_o1(self):
        conn = self.ftp._conn

        self.ftp._disconnect()

        self.assertFalse(self.ftp.connected())
        conn.close.assert_called_once()

    def test_upload_o0(self):
        self.ftp._upload("foo", "fobj")

        self.ftp._conn.storbinarydata.assert_called_once_with(
                "STOR foo", "fobj")

    def test_download_o0(self):
        fobj = Mock()
        self.ftp._download("foo", fobj)

        self.ftp._conn.retrbinary.assert_called_once_with(
                "RETR foo", fobj.write)

    def test_ls_o0(self):
        self.ftp._conn.nlst.return_value = "sthg"

        res = self.ftp._ls("foo")

        self.ftp._conn.nlst.assert_called_once_with("foo")
        self.assertEqual(res, "sthg")

    def test_is_file_o0(self):
        self.ftp._is_dir = Mock(return_value=True)

        res = self.ftp._is_file("foo")

        self.ftp._is_dir.assert_called_once_with("foo")
        self.assertNotEqual(res, True)

    def test_is_dir_o0(self):
        self.ftp._conn.cwd.side_effect = Exception

        res = self.ftp._is_dir("foo")

        self.ftp._conn.cwd.assert_called_with("foo")
        self.assertFalse(res)

    def test_is_dir_o1(self):
        res = self.ftp._is_dir("foo")

        self.ftp._conn.cwd.assert_any_call("foo")
        self.ftp._conn.cwd.assert_any_call(self.ftp._conn.pwd())
        self.assertTrue(res)

    def test_rm_o0(self):
        self.ftp._rm("foo")

        self.ftp._conn.delete.assert_called_with("foo")

    def test_rmdir_o0(self):
        self.ftp._rmdir("foo")

        self.ftp._conn.rmd.assert_called_with("foo")

    def test_mkdir_o0(self):
        self.ftp._mkdir("foo")

        self.ftp._conn.mkd.assert_called_with("foo")

    def test_mv_o0(self):
        self.ftp._mv("foo", "bar")

        self.ftp._conn.rename.assert_called_with("foo", "bar")


class TestFTP_TLS_DATA(unittest.TestCase):
    def test_storbinarydata(self):
        import ssl
        Mockconn = type("Mockconn", (Mock, ),
                        {"sendall": lambda self, buf: setattr(
                                    self, "sent", self.sent + buf)})
        conn = Mockconn(spec=ssl.SSLSocket)
        conn.sent = ""

        fobj = Mock()
        fobj.read.side_effect = ("foo", "bar", "baz", "")

        ftptls = FTP_TLS_Data()
        ftptls.transfercmd = Mock(return_value=conn)
        ftptls.voidcmd = Mock()
        ftptls.voidresp = Mock()

        ftptls.storbinarydata("cmd", fobj, callback=Mock())

        self.assertEqual(conn.sent, "foobarbaz")
        conn.close.assert_called_once()


class TestMisc(unittest.TestCase):
    def test_tweaked_join0(self):
        result = _tweaked_join("/a/b/c", "/d")
        result = os.path.normpath(result)
        self.assertEqual(result, "/a/b/c/d")

    def test_tweaked_join1(self):
        result = _tweaked_join("/a/b/c", "d/e")
        result = os.path.normpath(result)
        self.assertEqual(result, "/a/b/c/d/e")

    def test_tweaked_join2(self):
        result = _tweaked_join("C:\\a\\b", "/c/d")
        result = os.path.normpath(result)
        self.assertEqual(result, "C:/a/b/c/d")
