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
import os
from pathlib import Path

from modules.antivirus.base import AntivirusWindows

log = logging.getLogger(__name__)


class KasperskyWin(AntivirusWindows):
    name = "Kaspersky Anti-Virus (Windows)"

    # ==================================
    #  Constructor and destructor stuff
    # ==================================

    def __init__(self, *args, **kwargs):
        # class super class constructor
        super().__init__(*args, **kwargs)
        # scan tool variables
        self.scan_args = (
            "scan",  # scan command
            "/i0",   # report only
        )
        self._scan_retcodes[self.ScanResult.INFECTED] = lambda x: x in [2, 3]
        self.scan_patterns = [
            re.compile("^\S+\s+\S+"
                       "(?P<file>.+)\s+(detected|suspicion)\s+"
                       "(?P<name>.+)", re.IGNORECASE | re.MULTILINE),
        ]

    # ==========================================
    #  Antivirus methods (need to be overriden)
    # ==========================================

    def get_version(self):
        """return the version of the antivirus"""
        # Latest version do not output
        # version so extract it from path
        matches = re.search('Kaspersky Lab/Kaspersky Anti-Virus '
                            '(?P<version>\d+(\.\d+)+)/',
                            self.scan_path.as_posix(), re.IGNORECASE)
        if not matches:
            raise RuntimeError("Cannot read version in the path of the exec")
        return matches.group('version').strip()

    def get_database(self):
        """return list of files in the database"""
        # TODO: We list all files in Bases/*, heuristic to lookup database
        # must be improved
        search_paths = [Path(os.environ['PROGRAMDATA']) / "Kaspersky Lab/", ]
        database_patterns = [
            '*/Bases/*.avz',
            '*/Bases/*.dat',
            '*/Bases/*.dll',
            '*/Bases/*.esm',
            '*/Bases/*.kdc',
            '*/Bases/*.keb',
            '*/Bases/*.mft',
            '*/Bases/*.xms',
            '*/Bases/*.xml',
            '*/Bases/*.ini',
        ]
        return self.locate(database_patterns, search_paths, syspath=False)

    def get_scan_path(self):
        """return the full path of the scan tool"""
        return self.locate_one("Kaspersky Lab/*Anti-Virus*/avp.com")

    def get_virus_database_version(self):
        """return the db version of the antivirus"""
        regexp = 'AV bases release date: (?P<version>.+)'
        return self._run_and_parse(*self.scan_args,
                                   regexp=regexp,
                                   group='version')
