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


class Clam(AntivirusUnix):
    name = "Clam AntiVirus Scanner (Linux)"

    # ==================================
    #  Constructor and destructor stuff
    # ==================================

    def __init__(self, *args, **kwargs):
        # class super class constructor
        super().__init__(*args, **kwargs)
        # scan tool variables
        self.scan_args = (
            "--infected",    # only print infected files
            "--fdpass",      # avoid file access problem as clamdameon
                             # is runned by clamav user
            "--no-summary",  # disable summary at the end of scanning
            "--stdout",      # do not write to stderr
        )
        self.scan_patterns = [
            re.compile('(?P<file>.*): (?P<name>\S+) FOUND', re.IGNORECASE),
        ]

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
        # NOTE: we can use clamconf to get database location, but it is not
        # always installed by default. Instead, hardcode some common paths and
        # locate files using predefined patterns
        search_paths = [
            Path('/var/lib/clamav'),      # default location in debian
        ]
        database_patterns = [
            'main.cvd',
            'daily.c[lv]d',         # *.cld on debian and on
                                    # *.cvd on clamav website
            'bytecode.c[lv]d',      # *.cld on debian and on
                                    # *.cvd on clamav website
            'safebrowsing.c[lv]d',  # *.cld on debian and on
                                    # *.cvd on clamav website
            '*.hdb',                # clamav hash database
            '*.mdb',                # clamav MD5, PE-section based
            '*.ndb',                # clamav extended signature format
            '*.ldb',                # clamav logical signatures
        ]
        return self.locate(database_patterns, search_paths, syspath=False)

    def get_scan_path(self):
        """return the full path of the scan tool"""
        return self.locate_one("clamdscan")

    def get_virus_database_version(self):
        """Return the Virus Database version"""
        path = self.locate_one("freshclam")
        retcode, stdout, _ = self.run_cmd(path, '--version')
        if retcode:
            raise RuntimeError("Bad return code while getting dbversion")

        matches = re.search('\/(?P<version>\d+)\/',
                            stdout, re.IGNORECASE)
        if not matches:
            raise RuntimeError("Cannot read database version in stdout")

        return matches.group('version').strip()
