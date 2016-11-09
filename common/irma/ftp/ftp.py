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

from common.hash import sha256sum
from irma.common.exceptions import IrmaFtpError
import os


class IrmaFTP(object):
    """Irma generic FTP handler

    Parent class of IrmaSFTP and IrmaFTPS
    """

    # ==================================
    #  Constructor and Destructor stuff
    # ==================================
    def __init__(self, host, port, auth, key_path, user, passwd,
                 dst_user, upload_path):
        self._host = host
        self._port = port
        self._auth = auth
        self._key_path = key_path
        self._user = user
        self._passwd = passwd
        self._dst_user = dst_user
        self._upload_path = upload_path
        self._conn = None

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

    def _connect(self):
        raise NotImplementedError("This is a virtual class")

    def _disconnect(self):
        if self._conn is None:
            return
        try:
            self._conn.close()
        except Exception as e:
            raise IrmaFtpError("{0}".format(e))

    def _hash(self, fobj):
        # hash function for integrity
        # each uploaded file is renamed after its digest value
        # and checked at retrieval
        return sha256sum(fobj)

    def _check_hash(self, digest, fobj):
        if self._hash(fobj) != digest:
            raise IrmaFtpError("Integrity check file failed")

    def _tweaked_join(self, path1, path2):
        # Ensure path2 will not be treated as an absolute path
        # as os.path.join("/a/b/c","/") returns "/" and not "/a/b/c/"
        if path2.startswith("/"):
            path = os.path.join(path1, "." + path2)
        else:
            path = os.path.join(path1, path2)
        # Also ensure final path on windows does not contain "\"
        return path.replace("\\", "/")

    def _get_realpath(self, path):
        real_path = path
        if self._upload_path is not None:
            real_path = self._tweaked_join(self._upload_path, real_path)
        # if acting as a dst_user prefix path with
        # user home chroot
        if self._dst_user is not None:
            real_path = self._tweaked_join(self._dst_user, real_path)
        return real_path

    # ================
    #  Public methods
    # ================

    def upload_file(self, path, filename):
        """ Upload <filename> content into directory <path>"""
        try:
            with open(filename, 'rb') as src:
                dstname = self.upload_fobj(path, src)
            return dstname
        except Exception as e:
            raise IrmaFtpError("{0}".format(e))

    def download_file(self, path, remotename, dstname):
        """ Download <remotename> found in <path> to <dstname>"""
        try:
            with open(dstname, 'wb+') as dst:
                self.download_fobj(path, remotename, dst)
        except Exception as e:
            raise IrmaFtpError("{0}".format(e))
