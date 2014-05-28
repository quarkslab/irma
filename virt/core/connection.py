#
# Copyright (c) 2013-2014 QuarksLab.
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
import libvirt

from time import sleep
from common.oopatterns import ParametricSingleton
from virt.core.exceptions import ConnectionManagerError

log = logging.getLogger(__name__)


class ConnectionManager(ParametricSingleton):
    """
    Connection manager to a drive a local
    or remote virtual machine manager
    """

    handlers = {}

    # ============================
    #  parametric singleton stuff
    # ============================

    @staticmethod
    def depends_on(cls, *args, **kwargs):
        # singleton depends on the uri parameter
        (uri,) = args[0]
        return uri

    # ===========
    #  constants
    # ===========

    # Available drivers
    REMOTE = "remote"
    TEST = "test"

    XEN = "xen"
    QEMU = "qemu"
    VBOX = "vbox"

    LXC = "lxc"
    UML = "uml"
    OPENVZ = "openvz"

    HYPERV = "hyperv"
    POWERVM = "phyp"
    PARALLELS = "parallels"

    VMWARE_VPX = "vpx"
    VMWARE_ESX = "esx"
    VMWARE_GSX = "gsx"
    VMWARE_PLAYER = "vmwareplayer"
    VMWARE_WORKSTATION = "vmwarews"
    VMWARE_FUSION = "vmwarefusion"

    # Available transports
    TLS = "tls"
    UNIX = "unix"
    SSH = "ssh"
    EXT = "ext"
    TCP = "tcp"
    LIBSSH = "libssh2"

    # ==================================
    #  constructor and destructor stuff
    # ==================================

    def __init__(self, uri):
        """
        Instantiate a connection to the virtual
        machine manager specified by ``domainuri``

        :param uri: URI to reach the virtual machine manager
        :raises: ConnectionManagerError if ``uri`` provided
        is not a string or a valid URI
        """
        if not isinstance(uri, basestring):
            reason = ("'uri' argument must be supplied as a string, " +
                      "not as a {0}".format(type(uri)))
            raise ConnectionManagerError(reason)
        elif not ConnectionManager.validate_uri(uri):
            reason = "'uri' field value '{0}' is not valid".format(uri)
            raise ConnectionManagerError(reason)

        self._uri = uri

        self._drv = None
        self._drv = self._connect()

    def __del__(self):
        if self._drv:
            self._disconnect()

    # =======================
    #  context manager stuff
    # =======================

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.__del__()

    # ==================
    #  internal helpers
    # ==================

    def _connect(self):
        if self._drv:
            return self._drv
        self._drv = ConnectionManager.handlers.get(self._uri, None)
        if not self._drv:
            try:
                self._drv = libvirt.open(self._uri)
                ConnectionManager.handlers[self._uri] = self._drv
            except libvirt.libvirtError as e:
                raise ConnectionManagerError('{0}'.format(e))
        return self._drv

    def _disconnect(self):
        if self._drv:
            try:
                self._drv.close()
            except libvirt.libvirtError as e:
                raise ConnectionManagerError("{0}".format(e))
            finally:
                self._drv = None
                handler = ConnectionManager.handlers.pop(self._uri, None)
                if handler:
                    del handler

    def retry_connect(max_retries, delay):
        """function to try to reconnect"""

        def _retry_connect(func):
            """Outer function to try to reconnect"""

            def wrapper(self, *args, **kwargs):
                """Inner function to try to reconnect"""
                i = max_retries
                while not self._drv:
                    try:
                        self._reconnect()
                    except ConnectionManagerError as e:
                        if not i:
                            raise e
                        else:
                            i -= 1
                            time.sleep(delay)
                return func(self, *args, **kwargs)

            return wrapper

        return _retry_connect

    def _reconnect(self):
        """In case the connection drops, can be used to reconnect"""
        self._drv = None
        if self._uri in ConnectionManager.handlers:
            ConnectionManager.handlers.pop(self._uri)
        self._connect()

    # ================
    #  public methods
    # ================

    @property
    @retry_connect(10, 10)
    def connection(self):
        """returns the libvirt connection handle"""
        return self._drv

    @property
    def uri(self):
        """returns the libvirt connection handle"""
        return self._uri

    @staticmethod
    def create_uri(param):
        """create an uri from parameters passed in arguments

        :returns: a connection uri string
        :raises: NotImplementedError in any case
        .. versionadded:: 0.3
        """
        raise NotImplementedError("will be implemented in future versions")

    @staticmethod
    def validate_uri(uri):
        """checks if the uri passed is valid or not

        :returns: true if valid else false
        """
        # TODO: perform more type checking,
        # format checking and coherence checking
        valid = False
        if isinstance(uri, basestring):
            valid = True
        return valid

    @property
    @retry_connect(10, 10)
    def version(self):
        """get the libvirt version

        :returns: (major, minor, release) tuple
        """
        major, minor, release = None, None, None
        connection = self._drv
        if connection:
            version = connection.getLibVersion()
            # returned version is using the following format:
            # major * 1,000,000 + minor * 1,000 + release.
            major = (version / 1000000)
            minor = (version % 1000000) / 1000
            release = version % 1000
        return (major, minor, release)
