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

from ..base import Antivirus

log = logging.getLogger(__name__)


class AVGAntiVirusFree(Antivirus):

    # ==================================
    #  Constructor and destructor stuff
    # ==================================

    def __init__(self, *args, **kwargs):
        # class super class constructor
        super(AVGAntiVirusFree, self).__init__(*args, **kwargs)
        # set default antivirus information
        self._name = "AVG AntiVirus Free"
        # scan tool variables
        self._scan_args = (
            "--heur "      # use heuristics for scanning
            "--paranoid "  # Enable paranoid mode. Scan for less dangerous
                           # malware and more time consuming algoritms.
            "--arc "       # scan through archives
            "--macrow "    # report documents with macros.
            "--pwdw "      # report password protected files
            "--pup "       # scan for Potentially Unwanted Programs
        )
        self._scan_patterns = [
            re.compile(r'(?P<file>.*)'
                       r'\s+(Found|Virus found|Potentially harmful program|'
                       r'Virus identified|Trojan horse)\s+'
                       r'(?P<name>.*)(\\n)*.*$', re.IGNORECASE)
        ]
        # NOTE: do 'man avgscan' for return codes
        is_error_fn = lambda x: x in [1, 2, 3, 6, 7, 8, 9, 10]
        self._scan_retcodes[self.ScanResult.CLEAN] = lambda x: x in [0]
        self._scan_retcodes[self.ScanResult.INFECTED] = lambda x: x in [4, 5]
        self._scan_retcodes[self.ScanResult.ERROR] = lambda x: is_error_fn(x)

    # ==========================================
    #  Antivirus methods (need to be overriden)
    # ==========================================

    def get_version(self):
        """return the version of the antivirus"""
        result = None
        if self.scan_path:
            cmd = self.build_cmd(self.scan_path, '-v')
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
        # extract folder where are installed definition files
        avg_path = '/opt/avg/'
        # NOTE: the structure/location of the update folders are documented in
        # the /var/lib/avast/Setup/avast.setup script.
        search_paths = map(lambda x:
                           '{avg_path}/av/update/{folder}/'
                           ''.format(avg_path=avg_path, folder=x),
                           ['backup', 'download', 'prepare'])
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
        paths = self.locate("avgscan")
        return paths[0] if paths else None
