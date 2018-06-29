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


class McAfeeVSCL(AntivirusUnix):
    name = "McAfee VirusScan Command Line scanner (Linux)"

    # ==================================
    #  Constructor and destructor stuff
    # ==================================

    def __init__(self, *args, **kwargs):
        # class super class constructor
        super().__init__(*args, **kwargs)
        self.scan_args = (
            "--ASCII",             # display filenames as ASCII text
            "--ANALYZE",           # turn on heuristic analysis for
                                   # programs and macros
            "--MANALYZE",          # turn on macro heuristics
            "--MACRO-HEURISTICS",  # turn on macro heuristics
            "--RECURSIVE",         # examine any subdirectories
                                   # to the specified target directory.
            "--UNZIP",             # scan inside archive files
        )
        self._scan_retcodes[self.ScanResult.INFECTED] = lambda x: x not in [0]
        self.scan_patterns = [
            re.compile('(?P<file>\S+) \.\.\. '
                       'Found the (?P<name>[^!]+)!(.+)!{1,3}$',
                       re.IGNORECASE | re.MULTILINE),
            re.compile('(?P<file>\S+) \.\.\. '
                       'Found the (?P<name>[^!]+) [a-z]+ !{1,3}$',
                       re.IGNORECASE | re.MULTILINE),
            re.compile('(?P<file>\S+) \.\.\. '
                       'Found [a-z]+ or variant (?P<name>[^!]+) !{1,3}$',
                       re.IGNORECASE | re.MULTILINE),
            re.compile('(?P<file>\S*)'
                       '\s+\.\.\.\s+Found:\s+'
                       '(?P<name>\S.*(?=\s+NOT\s+a\s+virus\.))',
                       re.IGNORECASE),
        ]
        self.scan_path = Path("/usr/local/uvscan/uvscan")

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
            # default location in debian
            Path('/usr/local/uvscan'),
        ]
        database_patterns = [
            'avvscan.dat',   # data file for virus scanning
            'avvnames.dat',  # data file for virus names
            'avvclean.dat',  # data file for virus cleaning
        ]
        results = self.locate(database_patterns, search_paths, syspath=False)
        return results or None

    def get_virus_database_version(self):
        """Return the Virus Database version"""
        return self._run_and_parse(
            '--version',
            regexp='Dat set version: (?P<dbversion>[0-9]*)',
            group='dbversion')
