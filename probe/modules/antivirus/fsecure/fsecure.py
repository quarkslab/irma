#
# Copyright (c) 2013-2016 Quarkslab.
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
import stat
import tempfile

from ..base import Antivirus

log = logging.getLogger(__name__)


class FSecure(Antivirus):
    _name = "FSecure Antivirus (Linux)"

    # ==================================
    #  Constructor and destructor stuff
    # ==================================

    def __init__(self, *args, **kwargs):
        # class super class constructor
        super(FSecure, self).__init__(*args, **kwargs)
        # scan tool variables
        self._scan_args = (
            "--allfiles=yes ",
            "--scanexecutables=yes ",
            "--archive=yes ",
            "--mime=yes ",
            # "--riskware=yes ",
            "--virus-action1=report ",
            # "--riskware-action1=report ",
            "--suspected-action1=report ",
            "--virus-action2=none ",
            # "--riskware-action2=none ",
            "--suspected-action2=none ",
            "--auto=yes ",
            "--list=no ",
        )
        # see man zavcli for return codes
        # fsav reports the exit codes in following priority order:
        # 130, 7, 1, 3, 4, 8, 6, 9, 0.
        # 0 Normal exit; no viruses or suspicious files found.
        # 1 Fatal  error (Usually a missing or corrupted file.)
        # 3 A boot virus or file virus found.
        # 4 Riskware (potential spyware) found.
        # 6 At least one virus was removed and no infected files left.
        # 7 Out of memory.
        # 8 Suspicious files found (not necessarily infected by a virus)
        # 9 Scan error, at least one file scan failed.
        INFECTED = self.ScanResult.INFECTED
        ERROR = self.ScanResult.ERROR
        self._scan_retcodes[INFECTED] = lambda x: x in [3, 4, 6, 8]
        self._scan_retcodes[ERROR] = lambda x: x in [1, 7, 9]
        self._scan_patterns = [
            re.compile(r'(?P<file>.*)'
                       r':\s+(Infected|Suspected):\s+'
                       r'(?P<name>.*)', re.IGNORECASE),
        ]

    # ==========================================
    #  Antivirus methods (need to be overriden)
    # ==========================================

    def get_version(self):
        """return the version of the antivirus"""
        result = None
        if self.scan_path:
            cmd = self.build_cmd(self.scan_path, '--version')
            retcode, stdout, _ = self.run_cmd(cmd)
            if not retcode:
                matches = re.search(r'(?P<version>\d+([.-]\d+)+)',
                                    stdout,
                                    re.IGNORECASE)
                if matches:
                    result = matches.group('version').strip()
        return result

    def get_database(self):
        """return list of files in the database"""
        # TODO
        return None

    def get_scan_path(self):
        """return the full path of the scan tool"""
        paths = self.locate("fsav")
        return paths[0] if paths else None
