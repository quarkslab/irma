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
from irma.common.base.exceptions import IrmaSFTPError
from irma.common.ftp.ftp import FTPInterface
from paramiko import SFTPClient, Transport, RSAKey

import logging
logging.getLogger("paramiko").setLevel(logging.WARNING)


class IrmaSFTP(FTPInterface):
    """Irma SFTP handler

    This class handles the connection with a sftp server
    functions for interacting with it.
    """

    _Exception = IrmaSFTPError

    # ==================================
    #  Constructor and Destructor stuff
    # ==================================

    def __init__(self, host, port, auth, key_path, user, passwd,
                 dst_user=None, upload_path='uploads', hash_check=False,
                 autoconnect=True):
        self._conn = None
        self._client = None
        super().__init__(host, port, auth, key_path, user, passwd, dst_user,
                         upload_path, hash_check, autoconnect)

    def connected(self):
        return self._conn is not None

    # ============================
    #  Overridden private methods
    # ============================

    def _connect(self):
        self._conn = Transport((self._host, self._port))
        self._conn.window_size = pow(2, 27)
        self._conn.packetizer.REKEY_BYTES = pow(2, 32)
        self._conn.packetizer.REKEY_PACKETS = pow(2, 32)
        if self._auth == 'key':
            pkey = RSAKey.from_private_key_file(self._key_path)
            self._conn.connect(username=self._user, pkey=pkey)
        else:
            self._conn.connect(username=self._user, password=self._passwd)

        self._client = SFTPClient.from_transport(self._conn)

    def _disconnect(self, *, force=False):
        self._client = None
        if not force:
            self._conn.close()
        self._conn = None

    def _upload(self, remote, fobj):
        self._client.putfo(fobj, remote)

    def _download(self, remote, fobj):
        self._client.getfo(remote, fobj)

    def _ls(self, remote):
        return self._client.listdir(remote)

    def _is_file(self, remote):
        return not self._is_dir(remote)

    def _is_dir(self, remote):
        st = self._client.stat(remote)
        return stat.S_ISDIR(st.st_mode)

    def _rm(self, remote):
        self._client.remove(remote)

    def _rmdir(self, remote):
        self._client.rmdir(remote)

    def _mkdir(self, remote):
        self._client.mkdir(remote)

    def _mv(self, oldremote, newremote):
        self._client.rename(oldremote, newremote)
