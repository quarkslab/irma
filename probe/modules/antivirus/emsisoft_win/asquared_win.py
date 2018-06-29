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


class ASquaredCmdWin(AntivirusWindows):
    name = "Emsisoft Commandline Scanner (Windows)"

    # ==================================
    #  Constructor and destructor stuff
    # ==================================

    def __init__(self, *args, **kwargs):
        # class super class constructor
        super().__init__(*args, **kwargs)
        # scan tool variables
        self.scan_args = (
            "/h",
            "/r",
            "/a",
            "/n",
            "/f",
            "/s",
        )
        # scan tool variables
        self.scan_patterns = [
            re.compile('\s+(?P<file>.*)\s+detected:\s+(?P<name>.*\S)')
        ]

    # ==========================================
    #  Antivirus methods (need to be overriden)
    # ==========================================

    def get_version(self):
        """return the version of the antivirus"""
        return self._run_and_parse(
            regexp='(?P<version>\d+(\.\d+)+)',
            group='version')

    def get_database(self):
        """return list of files in the database"""
        # TODO: make locate() to be reccursive, and to extend selected folders
        patterns = [
            "/Emsisoft/a2cmd/Signatures/*",
            "/Emsisoft/a2cmd/Signatures/BD/*",
        ]
        return self.locate(patterns)

    def get_scan_path(self):
        """return the full path of the scan tool"""
        return self.locate_one("Emsisoft/a2cmd/a2cmd.exe")
