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

from modules.antivirus.base import AntivirusWindows

log = logging.getLogger(__name__)


class SophosWin(AntivirusWindows):
    name = "Sophos Endpoint Protection (Windows)"

    # ==================================
    #  Constructor and destructor stuff
    # ==================================

    def __init__(self, *args, **kwargs):
        # class super class constructor
        super().__init__(*args, **kwargs)
        # scan tool variables
        self.scan_args = (
            "-archive",   # scan inside archives
            "-cab",       # scan microsoft cab file
            "-loopback",  # scan loopback-type file
            "-tnef",      # scan tnet file
            "-mime",      # scan file encoded with mime format
            "-oe",        # scan microsoft outlook
            "-pua",       # scan file encoded with mime format
            "-ss",        # only print errors or found viruses
            "-nc",        # do not ask remove confirmation when infected
            "-nb",        # no bell sound
        )
        # NOTE: on windows, 0 can be returned even if the file is infected
        self._scan_retcodes[self.ScanResult.INFECTED] = \
                lambda x: x in [0, 1, 2, 3]
        self.scan_patterns = [
            re.compile(">>> Virus '(?P<name>.+)' found in file (?P<file>.+)",
                       re.IGNORECASE),
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
        database_patterns = [
            '*.dat',
            'vdl??.vdb',
            'sus??.vdb',
            '*.ide',
        ]
        database_patterns = ['Sophos/Sophos Anti-Virus/*/' + p
                             for p in database_patterns]
        return self.locate(database_patterns)

    def get_scan_path(self):
        """return the full path of the scan tool"""
        return self.locate_one("Sophos/Sophos Anti-Virus/sav32cli.exe")

    def get_virus_database_version(self):
        """Return the Virus Database version"""
        return self._run_and_parse(
            '--version',
            regexp='Virus data version *: *(?P<dbversion>\d+(\.\d+)+)',
            group='dbversion')
