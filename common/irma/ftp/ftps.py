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
from irma.common.exceptions import IrmaFTPSError, IrmaConfigurationError
from irma.ftp.ftp import IrmaFTP
from ftplib import FTP_TLS
import ssl
import os

log = logging.getLogger(__name__)


class FTP_TLS_Data(FTP_TLS):
    """
    Only improvement is to allow transfer of data
    directly instead of reading data from fp
    """

    def storbinarydata(self,
                       cmd,
                       fobj,
                       blocksize=2 ** 16,
                       callback=None,
                       rest=None):
        self.voidcmd('TYPE I')
        conn = self.transfercmd(cmd, rest)
        try:
            while 1:
                buf = fobj.read(blocksize)
                if len(buf) == 0:
                    break
                conn.sendall(buf)
                if callback:
                    callback(buf)
            # shutdown ssl layer
            if isinstance(conn, ssl.SSLSocket):
                conn.unwrap()
        finally:
            conn.close()
        return self.voidresp()


class IrmaFTPS(IrmaFTP):
    """Irma FTP/TLS handler

    This class handles the connection with a ftp server over tls
    functions for interacting with it.
    """
    # ==================================
    #  Constructor and Destructor stuff
    # ==================================
    def __init__(self, host, port, auth, key_path, user, passwd,
                 dst_user=None, upload_path=None, hash_check=False):
        if auth != "password":
            raise IrmaConfigurationError("key authentication not supported for"
                                         " FTPS")
        super(IrmaFTPS, self).__init__(host, port, auth, key_path, user,
                                       passwd, dst_user, upload_path,
                                       hash_check)
        # TODO support connection on non standard port
        if self._port != FTP_TLS.port:
            reason = ("connection supported " +
                      "only on port {0}".format(FTP_TLS.port))
            raise IrmaFTPSError(reason)
        self._connect()

    # =================
    #  Private methods
    # =================

    def _connect(self):
        if self._conn is not None:
            log.warn("Already connected to ftps server")
            return
        try:
            self._conn = FTP_TLS_Data(self._host, self._user, self._passwd)
            # Explicitly ask for secure data channel
            self._conn.prot_p()
        except Exception as e:
            raise IrmaFTPSError("{0}".format(e))

    # ================
    #  Public methods
    # ================

    def mkdir(self, path):
        try:
            dst_path = self._get_realpath(path)
            self._conn.mkd(dst_path)
        except Exception as e:
            raise IrmaFTPSError("{0}".format(e))
        return

    def list(self, path):
        """ list remote directory <path>"""
        try:
            dst_path = self._get_realpath(path)
            return self._conn.nlst(dst_path)
        except Exception as e:
            raise IrmaFTPSError("{0}".format(e))

    def upload_fobj(self, path, fobj):
        """ Upload <data> to remote directory <path>"""
        try:
            if self.hash_check:
                dstname = self._hash(fobj)
                path = os.path.join(path, dstname)
            dstpath = self._get_realpath(path)
            self._conn.storbinarydata("STOR {0}".format(dstpath),
                                      fobj)
            if self.hash_check:
                return dstname
        except Exception as e:
            raise IrmaFTPSError("{0}".format(e))

    def download_fobj(self, path, remotename, fobj):
        """ returns <remotename> found in <path>"""
        try:
            dstpath = self._get_realpath(path)
            dstpath = self._tweaked_join(dstpath, remotename)
            self._conn.retrbinary("RETR {0}".format(dstpath),
                                  lambda x: fobj.write(x))
            if self.hash_check:
                self._check_hash(remotename, fobj)
        except Exception as e:
            raise IrmaFTPSError("{0}".format(e))

    def delete(self, path, filename):
        """ Delete <filename> into directory <path>"""
        try:
            dstpath = self._get_realpath(path)
            full_dstpath = self._tweaked_join(dstpath, filename)
            self._conn.delete(full_dstpath)
        except Exception as e:
            raise IrmaFTPSError("{0}".format(e))

    def deletepath(self, path, deleteParent=False):
        # recursively delete all subdirs and files
        try:
            for f in self.list(path):
                if self.is_file(path, f):
                    self.delete(path, f)
                else:
                    self.deletepath(self._tweaked_join(path, f),
                                    deleteParent=True)
            if deleteParent:
                dstpath = self._get_realpath(path)
                self._conn.rmd(dstpath)
        except Exception as e:
            reason = "{0} [{1}]".format(e, path)
            raise IrmaFTPSError(reason)

    def is_file(self, path, filename):
        try:
            dstpath = self._get_realpath(path)
            pathfilename = self._tweaked_join(dstpath, filename)
            current = self._conn.pwd()
            self._conn.cwd(pathfilename)
            self._conn.cwd(current)
            return False
        except:
            return True

    def rename(self, oldpath, newpath):
        try:
            old_realpath = self._get_realpath(oldpath)
            new_realpath = self._get_realpath(newpath)
            self._conn.rename(old_realpath, new_realpath)
        except Exception as e:
            raise IrmaFTPSError("{0}".format(e))
