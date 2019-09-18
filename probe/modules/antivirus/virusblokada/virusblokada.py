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
from pathlib import Path

from modules.antivirus.base import AntivirusUnix

log = logging.getLogger(__name__)


class VirusBlokAda(AntivirusUnix):
    name = "VirusBlokAda Console Scanner (Linux)"

    # ==================================
    #  Constructor and destructor stuff
    # ==================================

    def __init__(self, *args, **kwargs):
        # class super class constructor
        super().__init__(*args, **kwargs)
        # scan tool variables
        self.scan_args = (
            "-AF+",   # all files
            # Displayed in help message but raises an error
            # "-PM+",   # thorough scanning mode
            "-RW+",   # detect Spyware, Adware, Riskware
            "-HA=3",  # heuristic analysis level
            "-VM+",   # show macros information in documents
            "-AR+",   # enable archives scanning
            "-ML+",   # mail scanning
            "-CH+",   # switch on cache while scanning objects
            "-SFX+",  # detect installers of malware
        )
        self._scan_retcodes[self.ScanResult.INFECTED] = lambda x: x in [6, 7]
        self.scan_patterns = [
            re.compile('(?P<file>\S+)'
                       '\s+(: infected)\s+'
                       '(?P<name>.+?)$', re.IGNORECASE | re.MULTILINE),
        ]

    # ==========================================
    #  Antivirus methods (need to be overriden)
    # ==========================================

    def get_version(self):
        """return the version of the antivirus"""
        return self._run_and_parse(
            '-h',
            regexp='(?P<version>\d+(\.\d+)+)',
            group='version')

    def get_database(self):
        """return list of files in the database"""
        # extract folder where are installed definition files
        search_paths = [
            # default location in debian
            Path('/opt/vba/vbacl/'),
        ]
        database_patterns = [
            '*.udb',  # data file for virus
            '*.lng',  # data file for virus
        ]
        return self.locate(database_patterns, search_paths, syspath=False)

    def get_scan_path(self):
        """return the full path of the scan tool"""
        return self.locate_one("vbacl")

    def get_virus_database_version(self):
        """Return the Virus Database version"""
        return self._run_and_parse(
            '-h',
            regexp='(?P<dbversion>\d+(\.\d+)+ \d\d:\d\d)',
            group='dbversion')
