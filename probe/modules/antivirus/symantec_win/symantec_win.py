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
import time

from datetime import date
from modules.antivirus.base import AntivirusWindows
from pathlib import Path

log = logging.getLogger(__name__)


class SymantecWin(AntivirusWindows):
    name = "Symantec Anti-Virus (Windows)"

    # ==================================
    #  Constructor and destructor stuff
    # ==================================

    def __init__(self, *args, **kwargs):
        # class super class constructor
        super().__init__(*args, **kwargs)
        # scan tool variables
        self.scan_args = (
            "/ScanFile",  # scan command
        )
        self.scan_patterns = [
            re.compile("^([^,]*,){6}(?P<name>[^,]+),(?P<file>[^,]+)",
                       re.IGNORECASE | re.MULTILINE),
        ]

    # ==========================================
    #  Antivirus methods (need to be overriden)
    # ==========================================

    def get_version(self):
        """return the version of the antivirus"""
        self._pdata_path = self.locate_one(
            "Symantec/Symantec Endpoint Protection/*.*/*",
            [Path(os.environ.get('PROGRAMDATA', '')), ],
            syspath=False)
        matches = re.search('(?P<version>\d+(\.\d+)+)',
                            self._pdata_path.as_posix(),
                            re.IGNORECASE)
        if matches is None:
            raise RuntimeError("Cannot read version in the pdata_path")
        return matches.group('version').strip()

    def get_scan_path(self):
        """return the full path of the scan tool"""
        return self.locate_one("Symantec/*/DoScan.exe")

    ##########################################################################
    # specific scan method
    ##########################################################################

    def scan(self, paths):
        log_name = date.today().strftime('%m%d%Y.log')
        self._log_path = self.locate_one(
                "Symantec/Symantec Endpoint Protection/*.*/" +
                "Data/Logs/AV/" + log_name,
                [Path(os.environ.get('PROGRAMDATA', '')), ],
                syspath=False)
        self._last_log_time = self._log_path.stat().st_mtime \
            if self._log_path.exists() else time.time()
        return super().scan(paths)

    def check_scan_results(self, paths, results):
        # TODO: clean up
        retcode, stdout, stderr = results[0], None, results[2]
        if self._log_path:
            # TODO: change the way results are fetched.
            # wait for log to be updated
            mtime = self._log_path.stat().st_mtime
            delay = 20
            while (mtime - self._last_log_time) <= 1 and delay != 0:
                time.sleep(0.5)
                mtime = self._log_path.stat().st_mtime
                delay -= 1
            # look for the line corresponding to this filename
            stdout = "".join(
                line + '\n'
                for line in self._log_path.read_text().splitlines()
                if ',' + paths.as_posix() + ',' in line)
            # force scan_result to consider it infected
            retcode = 1 if stdout else 0
            results = (retcode, stdout, stderr)
        return super().check_scan_results(paths, results)
