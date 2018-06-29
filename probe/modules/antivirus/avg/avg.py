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


class AVGAntiVirusFree(AntivirusUnix):
    name = "AVG AntiVirus Free (Linux)"

    # ==================================
    #  Constructor and destructor stuff
    # ==================================

    def __init__(self, *args, **kwargs):
        # class super class constructor
        super().__init__(*args, **kwargs)
        # scan tool variables
        self.scan_args = (
            "--heur",      # use heuristics for scanning
            "--paranoid",  # Enable paranoid mode. Scan for less dangerous
                           # malware and more time consuming algoritms.
            "--arc",       # scan through archives
            "--macrow",    # report documents with macros.
            "--pwdw",      # report password protected files
            "--pup",       # scan for Potentially Unwanted Programs
        )
        self.scan_patterns = [
            re.compile('(?P<file>\S+)\s+'
                       '(Found|Virus found|Potentially harmful program|'
                       'Virus identified|Trojan horse)\s+'
                       '(?P<name>.+)', re.IGNORECASE),
        ]

        # NOTE: do 'man avgscan' for return codes
        self._scan_retcodes = {
            self.ScanResult.CLEAN: lambda x: x in [0],
            self.ScanResult.INFECTED: lambda x: x in [4, 5],
            self.ScanResult.ERROR: lambda x: x in [1, 2, 3, 6, 7, 8, 9, 10],
        }

    # ==========================================
    #  Antivirus methods (need to be overriden)
    # ==========================================

    def get_version(self):
        """return the version of the antivirus"""
        return self._run_and_parse(
            '-v',
            regexp='(?P<version>\d+(\.\d+)+)',
            group='version')

    def get_database(self):
        """return list of files in the database"""
        # extract folder where are installed definition files
        avgdir = Path('/opt/avg/')
        # NOTE: the structure/location of the update folders are documented in
        # the /var/lib/avast/Setup/avast.setup script.
        search_paths = [avgdir / 'av/update' / d
                        for d in ['backup', 'download', 'prepare']]
        return self.locate('*', search_paths, syspath=False)

    def get_scan_path(self):
        """return the full path of the scan tool"""
        return self.locate_one("avgscan")

    def get_virus_database_version(self):
        """Return the Virus Database version"""
        path = self.locate_one("avgctl")
        retcode, stdout, _ = self.run_cmd(path, '--stat-all')
        if retcode:
            raise RuntimeError(
                "Bad return code while getting database version")
        matches = re.search('Virus database version *: *(?P<version>.*)',
                            stdout,
                            re.IGNORECASE)
        if not matches:
            raise RuntimeError("Cannot read database version in stdout")
        version = matches.group('version').strip()
        matches = re.search('Virus database release date *:.*, '
                            '(?P<date>\d\d \w+ \d\d\d\d)',
                            stdout,
                            re.IGNORECASE)
        if not matches:
            return version
        date = matches.group('date').strip()
        return version + ' (' + date + ')'
