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

from modules.antivirus.base import AntivirusWindows

log = logging.getLogger(__name__)


class McAfeeVSCLWin(AntivirusWindows):
    name = "McAfee VirusScan Command Line scanner (Windows)"

    # ==================================
    #  Constructor and destructor stuff
    # ==================================

    def __init__(self, *args, **kwargs):
        # class super class constructor
        super().__init__(*args, **kwargs)
        # scan tool variables
        self.scan_args = (
            "/ANALYZE",    # turn on heuristic analysis
                           # for program and macro
            "/MANALYZE",   # turn on macro heuristics
            "/RECURSIVE",  # examine any subdirectories in
                           # addition to the specified target directory.
            "/UNZIP",      # scan inside archives
            "/NOMEM",      # do not scan memory for viruses
        )
        # TODO: check for retcodes in WINDOWS
        self._scan_retcodes[self.ScanResult.INFECTED] = lambda x: x not in [0]
        self.scan_patterns = [
            re.compile('(?P<file>\S+) \.\.\. ' +
                       'Found the (?P<name>[^!]+)!(.+)!{1,3}$',
                       re.IGNORECASE | re.MULTILINE),
            re.compile('(?P<file>\S+) \.\.\. ' +
                       'Found the (?P<name>[^!]+) [a-z]+ !{1,3}$',
                       re.IGNORECASE | re.MULTILINE),
            re.compile('(?P<file>\S+) \.\.\. ' +
                       'Found [a-z]+ or variant (?P<name>[^!]+) !{1,3}$',
                       re.IGNORECASE | re.MULTILINE),
            re.compile('(?P<file>.*(?=\s+\.\.\.\s+Found:\s+))'
                       '\s+\.\.\.\s+Found:\s+'
                       '(?P<name>.*(?=\s+NOT\s+a\s+virus\.))',
                       re.IGNORECASE),
        ]
        self.scan_path = Path("C:/VSCL/scan.exe")

    # ==========================================
    #  Antivirus methods (need to be overriden)
    # ==========================================

    def get_version(self):
        """return the version of the antivirus"""
        return self._run_and_parse(
            '--version',
            regexp='(?P<version>\d+(\.\d+)+)',
            group='version')

    def get_database(self):
        """return list of files in the database"""
        search_paths = [
            # default install path in windows probes in irma
            Path('C:/VSCL')
        ]
        database_patterns = [
            'avvscan.dat',   # data file for virus scanning
            'avvnames.dat',  # data file for virus names
            'avvclean.dat',  # data file for virus cleaning
        ]
        return self.locate(database_patterns, search_paths, syspath=False)

    def get_virus_database_version(self):
        """Return the Virus Database version"""
        return self._run_and_parse(
            '/VERSION',
            regexp='AV Engine Version: (?P<dbversion>\d+\.\d+)',
            group='dbversion')
