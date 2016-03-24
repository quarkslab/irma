#
# Copyright (c) 2013-2016 Quarkslab.
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
import os
import stat
from irma.common.exceptions import IrmaSFTPError
from paramiko import SFTPClient, Transport

log = logging.getLogger(__name__)
logging.getLogger("paramiko").setLevel(logging.WARNING)


class IrmaSFTP(object):
    """Internal database.

    This class handles the conection with ftp server over tls
    functions for interacting with it.
    """
    # hash function for integrity
    # each uploaded file is renamed after its digest value
    # and checked at retrieval
    hashfunc = hashlib.sha256

    # ==================================
    #  Constructor and Destructor stuff
    # ==================================
    def __init__(self, host, port, user, passwd,
                 dst_user=None, upload_path='uploads'):
        self._host = host
        self._port = port
        self._user = user
        self._passwd = passwd
        self._conn = None
        self._client = None
        self._dst_user = dst_user
        self._upload_path = upload_path
        self._connect()

    def __del__(self):
        try:
            if self._conn is not None:
                self._disconnect()
        except AttributeError:
            # if exception raised in init
            # there is no _conn
            pass

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.__del__()

    # =================
    #  Private methods
    # =================

    def _connect(self):
        if self._conn is not None:
            log.warn("Already connected to sftp server")
            return
        try:
            self._conn = Transport((self._host, self._port))
            self._conn.connect(username=self._user, password=self._passwd)
            self._client = SFTPClient.from_transport(self._conn)
        except Exception as e:
            raise IrmaSFTPError("{0}".format(e))

    def _disconnect(self):
        if self._conn is None:
            return
        try:
            self._conn.close()
        except Exception as e:
            raise IrmaSFTPError("{0}".format(e))

    def _hash(self, data):
        try:
            return self.hashfunc(data).hexdigest()
        except Exception as e:
            raise IrmaSFTPError("{0}".format(e))

    def _check_hash(self, digest, data):
        try:
            if self.hashfunc(data).hexdigest() != digest:
                raise IrmaSFTPError("Integrity check file failed")
        except Exception as e:
            raise IrmaSFTPError("{0}".format(e))

    def _get_realpath(self, path):

        def tweaked_join(path1, path2):
            # Ensure path2 will not be treated as an absolute path
            # as os.path.join("/a/b/c","/") returns "/" and not "/a/b/c/"
            if path2.startswith("/"):
                return os.path.join(path1, "." + path2)
            else:
                return os.path.join(path1, path2)

        real_path = path
        if self._upload_path is not None:
            real_path = tweaked_join(self._upload_path, real_path)
        # if acting as a dst_user prefix path with
        # user home chroot
        if self._dst_user is not None:
            real_path = tweaked_join(self._dst_user, real_path)
        return real_path

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

    def upload_file(self, path, filename):
        """ Upload <filename> content into directory <path>"""
        try:
            with open(filename, 'rb') as f:
                dstname = self.upload_data(path, f.read())
            return dstname
        except Exception as e:
            raise IrmaSFTPError("{0}".format(e))

    def upload_data(self, path, data):
        """ Upload <data> to remote directory <path>"""
        try:
            dstname = self._hash(data)
            path = os.path.join(path, dstname)
            dstpath = self._get_realpath(path)
            with self._client.open(dstpath, 'wb') as dstfile:
                dstfile.write(data)
            return dstname
        except Exception as e:
            raise IrmaSFTPError("{0}".format(e))

    def download(self, path, remotename, dstname):
        """ Download <remotename> found in <path> to <dstname>"""
        try:
            dstpath = self._get_realpath(path)
            full_dstpath = os.path.join(dstpath, remotename)
            with self._client.open(full_dstpath, 'rb') as srcfile:
                buf = srcfile.read()
                # remotename is hashvalue of data
                self._check_hash(remotename, buf)
                with open(dstname, "wb") as f:
                    f.write(buf)
        except Exception as e:
            raise IrmaSFTPError("{0}".format(e))

    def download_data(self, path, remotename):
        """ returns <remotename> found in <path>"""
        try:
            dstpath = self._get_realpath(path)
            full_dstpath = os.path.join(dstpath, remotename)
            with self._client.open(full_dstpath, 'rb') as srcfile:
                buf = srcfile.read()
                # remotename is hashvalue of data
                self._check_hash(remotename, buf)
                return buf
        except Exception as e:
            raise IrmaSFTPError("{0}".format(e))

    def delete(self, path, filename):
        """ Delete <filename> into directory <path>"""
        try:
            dstpath = self._get_realpath(path)
            full_dstpath = os.path.join(dstpath, filename)
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
                    self.deletepath(os.path.join(path, f),
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
            full_dstpath = os.path.join(dstpath, filename)
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
