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


class Zoner(AntivirusUnix):
    name = "Zoner Antivirus (Linux)"

    # ==================================
    #  Constructor and destructor stuff
    # ==================================

    def __init__(self, *args, **kwargs):
        # class super class constructor
        super().__init__(*args, **kwargs)
        # scan tool variables
        self.scan_args = (
            "--scan-full",
            "--scan-heuristics",
            "--scan-emulation",
            "--scan-archives",
            "--scan-packers",
            "--scan-gdl",
            "--scan-deep",
            "--show=infected",
            "--quiet",
        )
        # see man zavcli for return codes
        self._scan_retcodes[self.ScanResult.ERROR] = lambda x: x in [1, 2, 16]
        self._scan_retcodes[self.ScanResult.INFECTED] = \
            lambda x: x in [
                11, 12, 13, 14, 15,  # documented codes
                -6  # undocumented codes
            ]
        self.scan_patterns = [
            re.compile('(?P<file>.*)'
                       ':\s+INFECTED\s+'
                       '\[(?P<name>[^\[]+)\]', re.IGNORECASE),
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
        # TODO: make locate() to be reccursive, and to extend selected folders
        zoner_path = Path("/opt/zav/")
        search_paths = [
            zoner_path / "/lib/",
            zoner_path / "/lib/modules/",
        ]

        database_patterns = [
            '*.so',
            '*.ver',
            '*.zdb',
        ]
        return self.locate(database_patterns, search_paths, syspath=False)

    def get_scan_path(self):
        """return the full path of the scan tool"""
        return self.locate_one("zavcli")

    def get_virus_database_version(self):
        """Return the Virus Database version"""
        return self._run_and_parse(
                '--version-zavd',
                regexp='ZAVDB version: *(?P<dbversion>.*)',
                group='dbversion')
