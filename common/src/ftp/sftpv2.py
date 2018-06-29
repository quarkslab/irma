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

import stat
import socket
from irma.common.base.exceptions import IrmaSFTPv2Error
from irma.common.ftp.ftp import FTPInterface
from ssh2.session import Session
from ssh2.sftp import LIBSSH2_FXF_CREAT, LIBSSH2_FXF_WRITE,\
                      LIBSSH2_SFTP_S_IRUSR, LIBSSH2_SFTP_S_IWUSR,\
                      LIBSSH2_SFTP_S_IRGRP, LIBSSH2_SFTP_S_IROTH,\
                      LIBSSH2_SFTP_S_IXUSR


class IrmaSFTPv2(FTPInterface):
    """Irma SFTPv2 handler

    This class handles the connection with a sftp server
    functions for interacting with it.
    """

    _Exception = IrmaSFTPv2Error

    # ==================================
    #  Constructor and Destructor stuff
    # ==================================

    def __init__(self, host, port, auth, key_path, user, passwd,
                 dst_user=None, upload_path='uploads', hash_check=False,
                 autoconnect=True):
        self._sess = None
        self._client = None
        super().__init__(host, port, auth, key_path, user, passwd, dst_user,
                         upload_path, hash_check, autoconnect)

    def connected(self):
        return self._sess is not None

    # ============================
    #  Overridden private methods
    # ============================

    def _connect(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self._host, self._port))
        self._sess = Session()
        self._sess.handshake(sock)
        if self._auth == 'key':
            # self._pubkey_path must be generated from private key
            # s.userauth_publickey_fromfile(self._user, self._pubkey_path,
            #                               self._key_path, '')
            raise IrmaSFTPv2Error("Pub key authentication not implemented")
        else:
            self._sess.userauth_password(self._user, self._passwd)
        self._client = self._sess.sftp_init()

    def _disconnect(self, *, force=False):
        self._client = None
        if not force:
            self._sess.disconnect()
        self._sess = None

    def _upload(self, remote, fobj):
        mode = LIBSSH2_SFTP_S_IRUSR | LIBSSH2_SFTP_S_IWUSR | \
            LIBSSH2_SFTP_S_IRGRP | LIBSSH2_SFTP_S_IROTH
        opt = LIBSSH2_FXF_CREAT | LIBSSH2_FXF_WRITE
        with self._client.open(remote, opt, mode) as rfh:
            for chunk in iter(lambda: fobj.read(1024*1024), b""):
                rfh.write(chunk)

    def _download(self, remote, fobj):
        with self._client.open(remote, 0, 0) as rfh:
            for size, data in rfh:
                fobj.write(data)

    def _ls(self, remote):
        with self._client.opendir(remote) as rfh:
            paths = (p[1].decode('utf-8') for p in rfh.readdir())
            return [p for p in paths if p not in ['.', '..']]

    def _is_file(self, remote):
        return not self._is_dir(remote)

    def _is_dir(self, remote):
        st = self._client.stat(remote)
        return stat.S_ISDIR(st.st_mode)

    def _rm(self, remote):
        self._client.unlink(remote)

    def _rmdir(self, remote):
        self._client.rmdir(remote)

    def _mkdir(self, remote):
        mode = LIBSSH2_SFTP_S_IRUSR | \
               LIBSSH2_SFTP_S_IWUSR | \
               LIBSSH2_SFTP_S_IXUSR
        self._client.mkdir(remote, mode)

    def _mv(self, oldremote, newremote):
        self._client.rename(oldremote, newremote)
