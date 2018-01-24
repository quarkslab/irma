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

from ..base import Antivirus

log = logging.getLogger(__name__)


class Clam(Antivirus):
    _name = "Clam AntiVirus Scanner (Linux)"

    # ==================================
    #  Constructor and destructor stuff
    # ==================================

    def __init__(self, *args, **kwargs):
        # class super class constructor
        super(Clam, self).__init__(*args, **kwargs)
        # scan tool variables
        self._scan_args = (
            "--infected "    # only print infected files
            "--fdpass "      # avoid file access problem as clamdameon
                             # is runned by clamav user
            "--no-summary "  # disable summary at the end of scanning
            "--stdout "      # do not write to stderr
        )
        self._scan_patterns = [
            re.compile(b'(?P<file>.*): (?P<name>[^\s]+) FOUND', re.IGNORECASE)
        ]

    # ==========================================
    #  Antivirus methods (need to be overriden)
    # ==========================================

    def get_version(self):
        """return the version of the antivirus"""
        result = None
        if self.scan_path:
            cmd = self.build_cmd(self.scan_path, '--version')
            retcode, stdout, stderr = self.run_cmd(cmd)
            if not retcode:
                matches = re.search(b'(?P<version>\d+(\.\d+)+)',
                                    stdout,
                                    re.IGNORECASE)
                if matches:
                    result = matches.group('version').strip()
        return result

    def get_database(self):
        """return list of files in the database"""
        # NOTE: we can use clamconf to get database location, but it is not
        # always installed by default. Instead, hardcode some common paths and
        # locate files using predefined patterns
        search_paths = [
            '/var/lib/clamav',      # default location in debian
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
        results = []
        for pattern in database_patterns:
            result = self.locate(pattern, search_paths, syspath=False)
            results.extend(result)
        return results if results else None

    def get_scan_path(self):
        """return the full path of the scan tool"""
        paths = self.locate("clamdscan")
        return paths[0] if paths else None

    def get_virus_database_version(self):
        """Return the Virus Database version"""
        paths = self.locate("freshclam")

        if paths:
            cmd = self.build_cmd(paths[0], '--version')
            retcode, stdout, stderr = self.run_cmd(cmd)

            if not retcode:
                matches = re.search(b'\/(?P<version>\d+)\/',
                                    stdout,
                                    re.IGNORECASE)

                if matches:
                    return matches.group('version').strip()

        return None
