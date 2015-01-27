#
# Copyright (c) 2013-2014 QuarksLab.
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


class Zoner(Antivirus):

    # ==================================
    #  Constructor and destructor stuff
    # ==================================

    def __init__(self, *args, **kwargs):
        # class super class constructor
        super(Zoner, self).__init__(*args, **kwargs)
        # set default antivirus information
        self._name = "Zoner Antivirus for Linux Desktop"
        # scan tool variables
        self._scan_args = (
            "--scan-full "
            "--scan-heuristics "
            "--scan-emulation "
            "--scan-archives "
            "--scan-packers "
            "--scan-gdl "
            "--scan-deep "
            "--show=infected "
            "--quiet "
        )
        # see man zavcli for return codes
        self._scan_retcodes[self.ScanResult.ERROR] = lambda x: x in [1, 2, 16]
        self._scan_retcodes[self.ScanResult.INFECTED] = \
            lambda x: x in [
                11, 12, 13, 14, 15,  # documented codes
                -6  # undocumented codes
            ]
        self._scan_patterns = [
            re.compile(r'(?P<file>.*)'
                       r':\s+INFECTED\s+'
                       r'\[(?P<name>[^\[]+)\]', re.IGNORECASE),
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
                matches = re.search(r'(?P<version>\d+([.-]\d+)+)',
                                    stdout,
                                    re.IGNORECASE)
                if matches:
                    result = matches.group('version').strip()
        return result

    def get_database(self):
        """return list of files in the database"""
        # extract folder where are installed definition files
        # TODO: make locate() to be reccursive, and to extend selected folders
        zoner_path = "/opt/zav/"
        search_paths = map(lambda x:
                           '{zoner_path}/lib/{folder}/'
                           ''.format(zoner_path=zoner_path, folder=x),
                           ['', 'modules'])
        database_patterns = [
            '*.so',
            '*.ver',
            '*.zdb',
        ]
        results = []
        for pattern in database_patterns:
            result = self.locate(pattern, search_paths, syspath=False)
            results.extend(result)
        return results if results else None

    def get_scan_path(self):
        """return the full path of the scan tool"""
        paths = self.locate("zavcli")
        return paths[0] if paths else None
