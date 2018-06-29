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
from datetime import datetime

from modules.antivirus.base import AntivirusUnix

log = logging.getLogger(__name__)


class EsetFileSecurity(AntivirusUnix):
    name = "ESET File Security (Linux)"

    # ==================================
    #  Constructor and destructor stuff
    # ==================================

    def __init__(self, *args, **kwargs):
        # class super class constructor
        super().__init__(*args, **kwargs)
        # Modify retun codes (see --help for details)
        self._scan_retcodes[self.ScanResult.INFECTED] = lambda x: x in [1, 50]
        self._scan_retcodes[self.ScanResult.ERROR] = lambda x: x in [100]
        # scan tool variables
        self.scan_args = (
            "--clean-mode=NONE",  # do not remove infected files
            "--no-log-all"        # do not log clean files
        )
        self.scan_patterns = [
           re.compile('name="(?P<file>.*)", threat="(?P<name>.*)", '
                      'action=.*', re.IGNORECASE),
        ]
        self.scan_path = Path("/opt/eset/esets/sbin/esets_scan")

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
            Path('/var/opt/eset/esets/lib/'),
        ]
        database_patterns = [
            '*.dat',  # determined using strace on linux
        ]
        return self.locate(database_patterns, search_paths, syspath=False)

    def get_virus_database_version(self):
        """Return the Virus Database version"""
        fdata = Path("/var/opt/eset/esets/lib/data/data.txt")
        data = fdata.read_text()

        matches = re.search('VerFileETAG_update\.eset\.com=(?P<version>.*)',
                            data, re.IGNORECASE)
        if not matches:
            raise RuntimeError(
                "Cannot read dbversion in {}".format(fdata.absolute()))
        version = matches.group('version').strip()

        matches = re.search('LastUpdate=(?P<date>\d*)', data, re.IGNORECASE)
        if not matches:
            raise RuntimeError(
                "Cannot read db date in {}".format(fdata.absolute()))
        date = matches.group('date').strip()
        date = datetime.fromtimestamp(int(date)).strftime('%Y-%m-%d')

        return version + ' (' + date + ')'
