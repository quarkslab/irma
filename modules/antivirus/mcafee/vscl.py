#
# Copyright (c) 2013-2015 QuarksLab.
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


class McAfeeVSCL(Antivirus):

    # ==================================
    #  Constructor and destructor stuff
    # ==================================

    def __init__(self, *args, **kwargs):
        # class super class constructor
        super(McAfeeVSCL, self).__init__(*args, **kwargs)
        # set default antivirus information
        self._name = "McAfee VirusScan Command Line scanner"
        # scan tool variables
        if self._is_windows:
            self._scan_args = (
                "/ANALYZE "    # turn on heuristic analysis
                               # for program and macro
                "/MANALYZE "   # turn on macro heuristics
                "/RECURSIVE "  # examine any subdirectories in
                               # addition to the specified target directory.
                "/UNZIP "      # scan inside archives
                "/NOMEM "      # do not scan memory for viruses
            )
        else:
            self._scan_retcodes[self.ScanResult.INFECTED] = \
                lambda x: x not in [0]
            self._scan_args = (
                "--ASCII "             # display filenames as ASCII text
                "--ANALYZE "           # turn on heuristic analysis for
                                       # programs and macros
                "--MANALYZE "          # turn on macro heuristics
                "--MACRO-HEURISTICS "  # turn on macro heuristics
                "--RECURSIVE "         # examine any subdirectories
                                       # to the specified target directory.
                "--UNZIP "             # scan inside archive files
            )
        # TODO: check for retcodes in WINDOWS
        self._scan_retcodes[self.ScanResult.INFECTED] = lambda x: x not in [0]
        self._scan_patterns = [
            re.compile(r'(?P<file>[^\s]+) \.\.\. ' +
                       r'Found the (?P<name>[^!]+)!(.+)\!{1,3}$',
                       re.IGNORECASE),
            re.compile(r'(?P<file>[^\s]+) \.\.\. ' +
                       r'Found the (?P<name>[^!]+) [a-z]+ \!{1,3}$',
                       re.IGNORECASE),
            re.compile(r'(?P<file>[^\s]+) \.\.\. ' +
                       r'Found [a-z]+ or variant (?P<name>[^!]+) \!{1,3}$',
                       re.IGNORECASE),
            re.compile(r'(?P<file>.*(?=\s+\.\.\.\s+Found:\s+))'
                       r'\s+\.\.\.\s+Found:\s+'
                       r'(?P<name>.*(?=\s+NOT\s+a\s+virus\.))',
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
                matches = re.search(r'(?P<version>\d+(\.\d+)+)',
                                    stdout,
                                    re.IGNORECASE)
                if matches:
                    result = matches.group('version').strip()
        return result

    def get_database(self):
        """return list of files in the database"""
        if self._is_windows:
            search_paths = [
                # default install path in windows probes in irma
                os.path.normpath('C:\VSCL')
            ]
        else:
            search_paths = [
                # default location in debian
                '/usr/local/uvscan',
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
        if self._is_windows:
            scan_bin = "scan.exe"
            scan_paths = os.path.normpath("C:\VSCL")
        else:
            scan_bin = "uvscan"
            scan_paths = os.path.normpath("/usr/local/uvscan/")
        paths = self.locate(scan_bin, scan_paths)
        return paths[0] if paths else None
