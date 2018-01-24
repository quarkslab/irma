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

from modules.antivirus.base import Antivirus

log = logging.getLogger(__name__)


class McAfeeVSCLWin(Antivirus):
    _name = "McAfee VirusScan Command Line scanner (Windows)"

    # ==================================
    #  Constructor and destructor stuff
    # ==================================

    def __init__(self, *args, **kwargs):
        # class super class constructor
        super(McAfeeVSCLWin, self).__init__(*args, **kwargs)
        # scan tool variables
        self._scan_args = (
            "/ANALYZE "    # turn on heuristic analysis
                           # for program and macro
            "/MANALYZE "   # turn on macro heuristics
            "/RECURSIVE "  # examine any subdirectories in
                           # addition to the specified target directory.
            "/UNZIP "      # scan inside archives
            "/NOMEM "      # do not scan memory for viruses
        )
        # TODO: check for retcodes in WINDOWS
        self._scan_retcodes[self.ScanResult.INFECTED] = lambda x: x not in [0]
        self._scan_patterns = [
            re.compile(b'(?P<file>[^\s]+) \.\.\. ' +
                       b'Found the (?P<name>[^!]+)!(.+)!{1,3}$',
                       re.IGNORECASE),
            re.compile(b'(?P<file>[^\s]+) \.\.\. ' +
                       b'Found the (?P<name>[^!]+) [a-z]+ !{1,3}$',
                       re.IGNORECASE),
            re.compile(b'(?P<file>[^\s]+) \.\.\. ' +
                       b'Found [a-z]+ or variant (?P<name>[^!]+) !{1,3}$',
                       re.IGNORECASE),
            re.compile(b'(?P<file>.*(?=\s+\.\.\.\s+Found:\s+))'
                       b'\s+\.\.\.\s+Found:\s+'
                       b'(?P<name>.*(?=\s+NOT\s+a\s+virus\.))',
                       re.IGNORECASE),
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
        search_paths = [
            # default install path in windows probes in irma
            os.path.normpath('C:\VSCL')
        ]
        database_patterns = [
            'avvscan.dat',   # data file for virus scanning
            'avvnames.dat',  # data file for virus names
            'avvclean.dat',  # data file for virus cleaning
        ]
        results = []
        for pattern in database_patterns:
            result = self.locate(pattern, search_paths, syspath=False)
            results.extend(result)
        return results if results else None

    def get_scan_path(self):
        """return the full path of the scan tool"""
        scan_bin = "scan.exe"
        scan_paths = os.path.normpath("C:\VSCL")
        paths = self.locate(scan_bin, scan_paths)
        return paths[0] if paths else None

    def get_virus_database_version(self):
        """Return the Virus Database version"""

        cmd = self.build_cmd(self.scan_path, '/VERSION')
        retcode, stdout, stderr = self.run_cmd(cmd)
        if retcode:
            raise RuntimeError(
                "Bad return code while getting database version")
        matches = re.search(b'AV Engine Version: (?P<version>\d+\.\d+)',
                            stdout,
                            re.IGNORECASE)
        if not matches:
            raise RuntimeError("Cannot read database version in stdout")
        return matches.group('version').strip()
