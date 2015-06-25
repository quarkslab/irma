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
import stat
import tempfile

from ..base import Antivirus

log = logging.getLogger(__name__)


class VirusBlokAda(Antivirus):

    # ==================================
    #  Constructor and destructor stuff
    # ==================================

    def __init__(self, *args, **kwargs):
        # class super class constructor
        super(VirusBlokAda, self).__init__(*args, **kwargs)
        # set default antivirus information
        self._name = "VirusBlokAda (Console Scanner)"
        # scan tool variables
        self._scan_args = (
            "-M=3 "   # action to take for an infected file
            "-AF+ "   # all files
            "-PM+ "   # thorough scanning mode
            "-RW+ "   # detect Spyware, Adware, Riskware
            "-HA=3 "  # heuristic analysis level
            "-VM+ "   # show macros information in documents
            "-AR+ "   # enable archives scanning
            "-ML+ "   # mail scanning
            "-CH+ "   # switch on cache while scanning objects
            "-SFX+ "  # detect installers of malware
        )
        self._scan_retcodes[self.ScanResult.INFECTED] = lambda x: x in [7]
        self._scan_patterns = [
            re.compile(r'(?P<file>[^\s]+)'
                       r'\s+(: infected)\s+'
                       r'(?P<name>[^\t]+)', re.IGNORECASE),
        ]

    # ==========================================
    #  Antivirus methods (need to be overriden)
    # ==========================================

    def get_version(self):
        """return the version of the antivirus"""
        result = None
        if self.scan_path:
            cmd = self.build_cmd(self.scan_path, '-h')
            retcode, stdout, stderr = self.run_cmd(cmd)
            if not retcode:
                matches = re.search(r'(?P<version>\d+(\.\d+)+)',
                                    stdout,
                                    re.IGNORECASE)
                if matches:
                    result = matches.group('version').strip()
        return result

    def get_database(self):
        """return list of files in the database"""
        # extract folder where are installed definition files
        results = []
        search_paths = [
            # default location in debian
            '/opt/vba/vbacl/',
        ]
        database_patterns = [
            '*.udb',  # data file for virus
            '*.lng',  # data file for virus
        ]
        for pattern in database_patterns:
            result = self.locate(pattern, search_paths, syspath=False)
            results.extend(result)
        return results if results else None

    def get_scan_path(self):
        """return the full path of the scan tool"""
        paths = self.locate("vbacl")
        return paths[0] if paths else None
