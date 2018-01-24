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
import os
import stat
from irma.common.exceptions import IrmaSFTPError
from irma.ftp.ftp import IrmaFTP
from paramiko import SFTPClient, Transport, RSAKey

log = logging.getLogger(__name__)
logging.getLogger("paramiko").setLevel(logging.WARNING)


class IrmaSFTP(IrmaFTP):
    """Irma SFTP handler

    This class handles the connection with a sftp server
    functions for interacting with it.
    """
    # ==================================
    #  Constructor and Destructor stuff
    # ==================================
    def __init__(self, host, port, auth, key_path, user, passwd,
                 dst_user=None, upload_path='uploads', hash_check=False):
        super(IrmaSFTP, self).__init__(host, port, auth, key_path, user,
                                       passwd, dst_user, upload_path,
                                       hash_check)
        self._client = None
        self._connect()

    # =================
    #  Private methods
    # =================

    def _connect(self):
        if self._conn is not None:
            log.warning("Already connected to sftp server")
            return
        try:
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
        except Exception as e:
            raise IrmaSFTPError("{0}".format(e))

    # ================
    #  Public methods
    # ================

    def mkdir(self, path):
        try:
            dst_path = self._get_realpath(path)
            self._client.mkdir(dst_path)
        except Exception as e:
            raise IrmaSFTPError("{0}".format(e))
        return

    def list(self, path):
        """ list remote directory <path>"""
        try:
            dst_path = self._get_realpath(path)
            return self._client.listdir(dst_path)
        except Exception as e:
            raise IrmaSFTPError("{0}".format(e))

    def upload_fobj(self, path, fobj):
        """ Upload <data> to remote destination
            if hash check is on:
                remote dest is <path>/<sha256 value>
            if hash check is off:
                remote dest is <path>
        """
        try:
            if self.hash_check:
                dstname = self._hash(fobj)
                path = self._tweaked_join(path, dstname)
            dstpath = self._get_realpath(path)
            self._client.putfo(fobj, dstpath)
            if self.hash_check:
                return dstname
        except Exception as e:
            raise IrmaSFTPError("{0}".format(e))

    def download_fobj(self, path, remotename, fobj):
        """ returns <remotename> found in <path>
            if hash check is on:
            remotename should be a <sha256 val> and
            will be compared after transfer
        """
        try:
            dstpath = self._get_realpath(path)
            full_dstpath = self._tweaked_join(dstpath, remotename)
            self._client.getfo(full_dstpath, fobj)
            if self.hash_check:
                # remotename is hashvalue of data
                self._check_hash(remotename, fobj)
        except Exception as e:
            raise IrmaSFTPError("{0}".format(e))

    def delete(self, path, filename):
        """ Delete <filename> into directory <path>"""
        try:
            dstpath = self._get_realpath(path)
            full_dstpath = self._tweaked_join(dstpath, filename)
            self._client.remove(full_dstpath)
        except Exception as e:
            raise IrmaSFTPError("{0}".format(e))

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
                self._client.rmdir(dstpath)
        except Exception as e:
            reason = "{0} [{1}]".format(str(e), path)
            raise IrmaSFTPError(reason)

    def is_file(self, path, filename):
        try:
            dstpath = self._get_realpath(path)
            full_dstpath = self._tweaked_join(dstpath, filename)
            st = self._client.stat(full_dstpath)
            return not stat.S_ISDIR(st.st_mode)
        except Exception as e:
            reason = "{0} [{1}]".format(e, path)
            raise IrmaSFTPError(reason)

    def rename(self, oldpath, newpath):
        try:
            old_realpath = self._get_realpath(oldpath)
            new_realpath = self._get_realpath(newpath)
            self._client.rename(old_realpath, new_realpath)
        except Exception as e:
            raise IrmaSFTPError("{0}".format(e))
