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


class Escan(Antivirus):
    _name = "eScan Antivirus (Linux)"

    # ==================================
    #  Constructor and destructor stuff
    # ==================================

    def __init__(self, *args, **kwargs):
        # class super class constructor
        super(Escan, self).__init__(*args, **kwargs)
        # scan tool variables
        self._scan_args = (
            "--log-only "
            "--recursion "
            "--pack "
            "--archives "
            "--heuristic "
            "--scan-ext "
            "--display-none "
            "--display-infected "
        )
        self._scan_retcodes[self.ScanResult.INFECTED] = lambda x: x in [0]
        self._scan_patterns = [
            re.compile(r'(?P<file>[^\s]+)'
                       r'\s+\[INFECTED\]'
                       r'\[(?P<name>[^\]]+)\]', re.IGNORECASE),
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
        escan_path = "/opt/MicroWorld/"
        search_paths = map(lambda x:
                           '{escan_path}/var/{folder}/'
                           ''.format(escan_path=escan_path, folder=x),
                           ['avsupd', 'bdplugins'])
        database_patterns = [
            '*',
        ]
        results = []
        for pattern in database_patterns:
            result = self.locate(pattern, search_paths, syspath=False)
            results.extend(result)
        return results if results else None

    def get_scan_path(self):
        """return the full path of the scan tool"""
        paths = self.locate("escan")
        return paths[0] if paths else None
