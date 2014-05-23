#
# Copyright (c) 2014 QuarksLab.
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

from modules.antivirus.base import Antivirus

log = logging.getLogger(__name__)


class EsetNod32(Antivirus):

    # ==================================
    #  Constructor and destructor stuff
    # ==================================

    def __init__(self, *args, **kwargs):
        # class super class constructor
        super(EsetNod32, self).__init__(*args, **kwargs)
        # set default antivirus information
        self._name = "ESET NOD32 Antivirus Business Edition for Linux Desktop"
        # Modify retun codes (see --help for details)
        self._scan_retcodes[self.ScanResult.INFECTED] = lambda x: x in [1, 50]
        # scan tool variables
        self._scan_args = (
            "--clean-mode=NONE "  # do not remove infected files
            "--no-log-all"        # do not log clean files
        )
        self._scan_patterns = [
            re.compile(r'name="(?P<file>.*)", threat="(?P<name>.*)", action=.*',
                       re.IGNORECASE | re.MULTILINE)
        ]

    # ==========================================
    #  Antivirus methods (need to be overriden)
    # ==========================================

    def get_version(self):
        """return the version of the antivirus"""
        result = None
        if self.scan_path:
            cmd = self.build_cmd(self.scan_path, '--version')
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
        search_paths = [
            '/var/opt/eset/esets/lib/',
        ]
        database_patterns = [
            '*.dat',  # determined using strace on linux
        ]
        results = []
        for pattern in database_patterns:
            result = self.locate(pattern, search_paths, syspath=False)
            results.extend(result)
        return results if results else None

    def get_scan_path(self):
        """return the full path of the scan tool"""
        paths = self.locate("esets_scan", "/opt/eset/esets/sbin/")
        return paths[0] if paths else None
