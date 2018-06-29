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

from irma.common.utils.hash import sha256sum
from irma.common.base.exceptions import IrmaFtpError
import os
import abc

import logging
log = logging.getLogger(__name__)


class FTPInterface(abc.ABC):
    """ Irma generic FTP handler
    Defines logic and error handling for its subclasses.

    Defines two ways to open a connection:
    >>> with IrmaFTPS(...) as ftp:
    ...     [...]

    >>> ftp = IrmaFTPS(..., connect=False)
    >>> with ftp.connect():
    ...     [...]
    >>> with ftp.connect():
    ...     [...]
    """

    _Exception = IrmaFtpError

    # ==================================
    #  Constructor and Destructor stuff
    # ==================================

    def __init__(self, host, port, auth, key_path, user, passwd,
                 dst_user, upload_path, hash_check, autoconnect):
        self._host = host
        self._port = port
        self._auth = auth
        self._key_path = key_path
        self._user = user
        self._passwd = passwd
        self._dst_user = dst_user
        self._upload_path = upload_path
        self.hash_check = hash_check
        if autoconnect:
            self.connect()

    def __del__(self):
        if self.connected():
            self.disconnect()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        if self.connected():
            self.disconnect()

    # ================
    #  Public methods
    # ================

    def connect(self):
        if self.connected():
            log.warn("Cannot open connection: already connected")
            return
        try:
            self._connect()

            # necessary to be able to
            # >>> with ftp.connect():
            # ...     [...]
            return self
        except Exception as e:
            raise self._Exception("{0}".format(e))

    def disconnect(self):
        if not self.connected():
            log.warn("Cannot close connection: not connected")
            return
        try:
            self._disconnect()
        except Exception as e:
            log.error("Cannot gracefully disconnect, force disconnection...")
            self._disconnect(force=True)
            raise self._Exception("{0}".format(e))

    def upload_file(self, path, filename):
        """ Upload <filename> content into directory <path>"""
        with open(filename, 'rb') as src:
            dstname = self.upload_fobj(path, src)
            return dstname

    def download_file(self, path, remotename, dstname):
        """ Download <remotename> found in <path> to <dstname>"""
        with open(dstname, 'wb+') as dst:
            self.download_fobj(path, remotename, dst)

    def upload_fobj(self, path, fobj):
        """ Upload <data> to remote directory <path>"""
        try:
            if self.hash_check:
                dstname = self._hash(fobj)
                path = os.path.join(path, dstname)
            dstpath = self._get_realpath(path)
            self._upload(dstpath, fobj)
            if self.hash_check:
                return dstname
        except Exception as e:
            raise self._Exception("{0}".format(e))

    def download_fobj(self, path, remotename, fobj):
        """ returns <remotename> found in <path>"""
        try:
            dstpath = self._get_realpath(path)
            dstpath = _tweaked_join(dstpath, remotename)
            self._download(dstpath, fobj)
            if self.hash_check:
                self._check_hash(remotename, fobj)
        except Exception as e:
            raise self._Exception("{0}".format(e))

    def list(self, path):
        """ list remote directory <path>"""
        try:
            dst_path = self._get_realpath(path)
            return self._ls(dst_path)
        except Exception as e:
            raise self._Exception("{0}".format(e))

    def is_file(self, path, filename):
        try:
            dstpath = self._get_realpath(path)
            full_dstpath = _tweaked_join(dstpath, filename)
            return self._is_file(full_dstpath)
        except Exception as e:
            reason = "{0} [{1}]".format(e, path)
            raise self._Exception(reason)

    def delete(self, path, filename):
        """ Delete <filename> into directory <path>"""
        try:
            dstpath = self._get_realpath(path)
            full_dstpath = _tweaked_join(dstpath, filename)
            self._rm(full_dstpath)
        except Exception as e:
            raise self._Exception("{0}".format(e))

    def mkdir(self, path):
        try:
            dst_path = self._get_realpath(path)
            self._mkdir(dst_path)
        except Exception as e:
            raise self._Exception("{0}".format(e))

    def rename(self, oldpath, newpath):
        try:
            old_realpath = self._get_realpath(oldpath)
            new_realpath = self._get_realpath(newpath)
            self._mv(old_realpath, new_realpath)
        except Exception as e:
            raise self._Exception("{0}".format(e))

    # =================
    #  Abstract methods
    # ==================
    #  should be implemented by every subclass

    @abc.abstractmethod
    def _connect(self):
        pass  # pragma: no cover

    @abc.abstractmethod
    def _disconnect(self, *, force=False):
        pass  # pragma: no cover

    @abc.abstractmethod
    def connected(self):
        pass  # pragma: no cover

    @abc.abstractmethod
    def _upload(self, remote, fobj):
        """ Upload local fobj to a remote path"""
        pass  # pragma: no cover

    @abc.abstractmethod
    def _download(self, remote, fobj):
        """ Download a remote path to the local fobj"""
        pass  # pragma: no cover

    @abc.abstractmethod
    def _ls(self, remote):
        """ List filenames of the remote directory contents"""
        pass  # pragma: no cover

    @abc.abstractmethod
    def _is_file(self, remote):
        """ Predicate.
        Returns True if the remote path points to a regular file"""
        pass  # pragma: no cover

    @abc.abstractmethod
    def _is_dir(self, remote):
        """ Predicate.
        Returns True if the remote path points to a directory"""
        pass  # pragma: no cover

    @abc.abstractmethod
    def _rm(self, remote):
        """ Remove a remote path if it points to a regular file"""
        pass  # pragma: no cover

    @abc.abstractmethod
    def _rmdir(self, remote):
        """ Remove a remote path if it points to a directory"""
        pass  # pragma: no cover

    @abc.abstractmethod
    def _mkdir(self, remote):
        """ Create a new directory in the remote tree"""
        pass  # pragma: no cover

    @abc.abstractmethod
    def _mv(self, oldremote, newremote):
        """ Move a filesystem item"""
        pass  # pragma: no cover

    # =================
    #  Private methods
    # =================

    @classmethod
    def _hash(cls, fobj):
        # hash function for integrity
        # each uploaded file is renamed after its digest value
        # and checked at retrieval
        return sha256sum(fobj)

    @classmethod
    def _check_hash(cls, digest, fobj):
        if cls._hash(fobj) != digest:
            raise cls._Exception("Integrity check file failed")

    def _get_realpath(self, path):
        real_path = path
        if self._upload_path is not None:
            real_path = _tweaked_join(self._upload_path, real_path)
        # if acting as a dst_user prefix path with
        # user home chroot
        if self._dst_user is not None:
            real_path = _tweaked_join(self._dst_user, real_path)
        return real_path


def _tweaked_join(path1, path2):
    # Ensure path2 will not be treated as an absolute path
    # as os.path.join("/a/b/c","/") returns "/" and not "/a/b/c/"
    if path2.startswith("/"):
        path = os.path.join(path1, "." + path2)
    else:
        path = os.path.join(path1, path2)
    # Also ensure final path on windows does not contain "\"
    return path.replace("\\", "/")
