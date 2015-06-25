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

from ..base import Antivirus

log = logging.getLogger(__name__)


class ComodoCAVL(Antivirus):

    # ==================================
    #  Constructor and destructor stuff
    # ==================================

    def __init__(self, *args, **kwargs):
        # class super class constructor
        super(ComodoCAVL, self).__init__(*args, **kwargs)
        # set default antivirus information
        self._name = "Comodo Antivirus for Linux"
        # Comodo does not use return value as infection indicator
        self._scan_retcodes[self.ScanResult.INFECTED] = lambda x: x in [0]
        # scan tool variables
        self._scan_args = (
            "-v ",  # verbose mode, display more detailed output
            "-s ",  # scan a file or directory
        )
        self._scan_patterns = [
            re.compile(r'(?P<file>.*) ---\> Found .*,' +
                       r' Malware Name is (?P<name>.*)', re.IGNORECASE)
        ]

    # ==========================================
    #  Antivirus methods (need to be overriden)
    # ==========================================

    def get_version(self):
        """return the version of the antivirus"""
        result = None
        if self.scan_path:
            dirname = os.path.dirname(self.scan_path)
            version_file = self.locate('cavver.dat', dirname)
            if version_file:
                with open(version_file[0], 'rb') as file:
                    result = file.read().strip()
        return result

    def get_database(self):
        """return list of files in the database"""
        result = None
        if self.scan_path:
            dirname = os.path.dirname(self.scan_path)
            database_path = self.locate('scanners/*.cav',
                                        dirname,
                                        syspath=False)
            result = database_path
        return result

    def get_scan_path(self):
        """return the full path of the scan tool"""
        paths = self.locate("cmdscan", "/opt/COMODO")
        return paths[0] if paths else None

    def scan(self, paths):
        # override scan as comodo uses only absolute paths, we need to convert
        # provided paths to absolute paths first
        paths = os.path.abspath(paths)
        return super(ComodoCAVL, self).scan(paths)
