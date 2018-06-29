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
import re

from modules.antivirus.base import AntivirusWindows

log = logging.getLogger(__name__)


class AviraWin(AntivirusWindows):
    name = "Avira Anti-Virus (Windows)"

    # ==================================
    #  Constructor and destructor stuff
    # ==================================

    def __init__(self, *args, **kwargs):
        # class super class constructor
        super().__init__(*args, **kwargs)
        # scan tool variables
        # other flag
        # archivemaxrecursion=N default 10
        self.scan_args = (
            "--nombr",  # do not check any master boot records
            "/z",  # scan in archives
            "/a",  # scan all files
            "/n",  # no-recursion
            # heuristic level (0 == off, 1 == low, 2 == medium, 3 == high)
            "--heurlevel=0",
        )
        # return code
        # 0 Normal nothing found
        # 1 Found converning file
        # 3 Suspicious files found (maybe need regex for this one and I think
        # is used when heurlevel is set)
        self._scan_retcodes[self.ScanResult.INFECTED] = lambda x: x in [1, 3]
        self.scan_patterns = [
            re.compile(" ALERT:\s+\[(?P<name>.*)\] (?P<file>.*)\s+<"),
        ]

    # ==========================================
    #  Antivirus methods (need to be overriden)
    # ==========================================
    def get_version(self):
        """return the version of the antivirus"""
        return self._run_and_parse(
            '/v',
            regexp='engine set:\s+(?P<version>\d+(\.\d+)+)',
            group='version')
        # match VDF version is for database
        # matches = re.search(r'VDF Version:\s+'
        #                     r'(?P<version>\d+(\.\d+)+)',
        #                    stdout, re.IGNORECASE)
        # match engine version

    def get_database(self):
        """return list of files in the database"""
        return self.locate("Avira/scancl/*.vdf")

    def get_scan_path(self):
        """return the full path of the scan tool"""
        return self.locate_one("Avira/*/scancl.exe")
