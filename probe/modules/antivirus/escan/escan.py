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


class Escan(AntivirusUnix):
    name = "eScan Antivirus (Linux)"

    # ==================================
    #  Constructor and destructor stuff
    # ==================================

    def __init__(self, *args, **kwargs):
        # class super class constructor
        super().__init__(*args, **kwargs)
        # scan tool variables
        self.scan_args = (
            "--log-only",
            "--recursion",
            "--pack",
            "--archives",
            "--heuristic",
            "--scan-ext",
            "--display-none",
            "--display-infected",
        )
        # Escan does not use return value as infection indicator. Distinction
        # between INFECTED and CLEAN will be done in the 'false positive
        # handler' of Antivirus.scan()
        self._scan_retcodes[self.ScanResult.INFECTED] = lambda x: x in [0]
        self.scan_patterns = [
                re.compile('^(?P<file>\S+?)\s+\[INFECTED\]\[(?P<name>.*)\]$',
                       re.IGNORECASE | re.MULTILINE),
        ]

    # ==========================================
    #  Antivirus methods (need to be overriden)
    # ==========================================

    def get_version(self):
        """return the version of the antivirus"""
        return self._run_and_parse(
            '--version',
            regexp='(?P<version>\d+([.-]\d+)+)',
            group='version')

    def get_database(self):
        """return list of files in the database"""
        # extract folder where are installed definition files
        escandir = Path("/opt/MicroWorld/")
        search_paths = [
                escandir / "var/avsupd",
                escandir / "var/bdplugins",
        ]
        return self.locate('*', search_paths, syspath=False)

    def get_scan_path(self):
        """return the full path of the scan tool"""
        return self.locate_one("escan")

    def get_virus_database_version(self):
        """Return the Virus Database version"""
        retcode, stdout, _ = self.run_cmd(self.scan_path, '-ui')
        if retcode:
            raise RuntimeError(
                "Bad return code while getting database version")
        matches = re.search('Anti-virus Engine Version : *'
                            '(?P<version>\d*\.\d*)',
                            stdout,
                            re.IGNORECASE)
        if not matches:
            raise RuntimeError("Cannot read database version in stdout")
        version = matches.group('version').strip()
        matches = re.search('Date of Virus Signature *: *'
                            '(?P<date>\d\d/\d\d/\d\d\d\d)',
                            stdout,
                            re.IGNORECASE)
        if not matches:
            return version
        date = matches.group('date').strip()
        return version + ' (' + date + ')'
