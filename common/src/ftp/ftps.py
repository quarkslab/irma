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

import ssl
from ftplib import FTP_TLS
from irma.common.base.exceptions import IrmaFTPSError, IrmaConfigurationError
from irma.common.ftp.ftp import FTPInterface


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


class IrmaFTPS(FTPInterface):
    """Irma FTP/TLS handler

    This class handles the connection with a ftp server over tls
    functions for interacting with it.
    """

    _Exception = IrmaFTPSError

    # ==================================
    #  Constructor and Destructor stuff
    # ==================================

    def __init__(self, host, port, auth, key_path, user, passwd,
                 dst_user=None, upload_path=None, hash_check=False,
                 autoconnect=True):
        self._conn = None
        if auth != "password":
            raise IrmaConfigurationError("key authentication not supported for"
                                         " FTPS")
        # TODO support connection on non standard port
        if port != FTP_TLS.port:
            reason = ("connection supported " +
                      "only on port {0}".format(FTP_TLS.port))
            raise IrmaFTPSError(reason)
        super().__init__(host, port, auth, key_path, user, passwd, dst_user,
                         upload_path, hash_check, autoconnect)

    def connected(self):
        return self._conn is not None

    # ============================
    #  Overridden private methods
    # ============================

    def _connect(self):
        self._conn = FTP_TLS_Data(self._host, self._user, self._passwd)
        # Explicitly ask for secure data channel
        self._conn.prot_p()

    def _disconnect(self, *, force=False):
        if not force:
            self._conn.close()
        self._conn = None

    def _upload(self, remote, fobj):
        self._conn.storbinarydata("STOR {0}".format(remote), fobj)

    def _download(self, remote, fobj):
        self._conn.retrbinary("RETR {0}".format(remote), fobj.write)

    def _ls(self, remote):
        return self._conn.nlst(remote)

    def _is_file(self, remote):
        return not self._is_dir(remote)

    def _is_dir(self, remote):
        try:
            oldcwd = self._conn.pwd()
            self._conn.cwd(remote)
            self._conn.cwd(oldcwd)
            return True
        except Exception:
            return False

    def _rm(self, remote):
        self._conn.delete(remote)

    def _rmdir(self, remote):
        self._conn.rmd(remote)

    def _mkdir(self, remote):
        self._conn.mkd(remote)

    def _mv(self, oldremote, newremote):
        self._conn.rename(oldremote, newremote)
