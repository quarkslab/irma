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


class Kaspersky(Antivirus):

    # ==================================
    #  Constructor and destructor stuff
    # ==================================

    def __init__(self, *args, **kwargs):
        # class super class constructor
        super(Kaspersky, self).__init__(*args, **kwargs)
        # set default antivirus information
        self._name = "Kaspersky Anti-Virus"
        # scan tool variables
        self._scan_args = (
            "scan "  # scan command
            "/i0 "   # report only
        )
        self._scan_retcodes[self.ScanResult.INFECTED] = lambda x: x in [2, 3]
        self._scan_patterns = [
            re.compile(r"^[^\s]+\s+[^\s]+" +
                       r"(?P<file>.+)\s+(detected|suspicion)+" +
                       r"\s(?P<name>[^\r]*)")
        ]

    # ==========================================
    #  Antivirus methods (need to be overriden)
    # ==========================================

    def get_version(self):
        """return the version of the antivirus"""
        result = None
        if self.scan_path:
            cmd = self.build_cmd(self.scan_path, 'help')
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
        # TODO: We list all files in Bases/*, heuristic to lookup database
        # must be improved
        search_paths = map(lambda x:
                           "{path}/Kaspersky Lab/*/Bases".format(path=x),
                           [os.environ.get('PROGRAMDATA', '')])
        database_patterns = [
            '*.avz',
            '*.dat',
            '*.dll',
            '*.esm',
            '*.kdc',
            '*.keb',
            '*.mft',
            '*.xms',
            '*.xml',
            '*.ini',
        ]
        results = []
        for pattern in database_patterns:
            result = self.locate(pattern, search_paths, syspath=False)
            results.extend(result)
        return results if results else None

    def get_scan_path(self):
        """return the full path of the scan tool"""
        scan_bin = "avp.com"
        scan_paths = map(lambda x: "{path}/Kaspersky Lab/*".format(path=x),
                         [os.environ.get('PROGRAMFILES', ''),
                          os.environ.get('PROGRAMFILES(X86)', '')])
        paths = self.locate(scan_bin, scan_paths)
        return paths[0] if paths else None
