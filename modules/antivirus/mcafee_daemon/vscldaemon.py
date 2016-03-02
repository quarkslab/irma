#
# Copyright (c) 2013-2015 QuarksLab.
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
import re
import os
import socket
from ..mcafee.vscl import McAfeeVSCL

from modules.antivirus.base import Antivirus

log = logging.getLogger(__name__)


class McAfeeDaemon(McAfeeVSCL):
    _daemon_config = '/etc/mcafee-daemon/server.ini'
    # ==================================
    #  Constructor and destructor stuff
    # ==================================

    def __init__(self, *args, **kwargs):
        # class super class constructor
        super(McAfeeDaemon, self).__init__(*args, **kwargs)
        # set default antivirus information
        self._name = "McAfee VirusScan Daemon"
        self._socket_path = kwargs.get("socket_path", None)

    def scan(self, paths):
        # reset result to an empty dictionary
        self._scan_results = dict()
        # check if patterns are set
        if not self.scan_patterns:
            raise ValueError("scan_patterns not defined")
        if self._socket_path is None:
            raise ValueError("No socket path set")
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect(self._socket_path)
        s.send(os.path.abspath(paths) + "\n")
        fs = s.makefile()
        res = fs.readline().strip()
        log.warning("Daemon reply {0}".format(res))
        # Let simulate a retcode
        if res == "UNINFECTED":
            results = (0, res, None)
        else:
            results = (1, "{0} {1}".format(paths, res), None)
        return self.check_scan_results(paths, results)
