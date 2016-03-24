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

from modules.antivirus.base import Antivirus

log = logging.getLogger(__name__)


class Avira(Antivirus):

    # ==================================
    #  Constructor and destructor stuff
    # ==================================

    def __init__(self, *args, **kwargs):
        # class super class constructor
        super(Avira, self).__init__(*args, **kwargs)
        # set default antivirus information
        self._name = "Avira Anti-Virus"
        # scan tool variables
        # other flag
        # archivemaxrecursion=N default 10
        self._scan_args = (
            "--nombr",  # do not check any master boot records
            "/z",  # scan in archives
            "/a",  # scan all files
            "/n",  # no-recursion
            # heuristic level (0 == off, 1 == low, 2 == medium, 3 == high)
            "--heurlevel=0",
        )
        # return code
        # 0 Normal nothing found
        # 1 Found converning file
        # 3 Suspicious files found (maybe need regex for this one and I think
        # is used when heurlevel is set)
        self._scan_retcodes[self.ScanResult.INFECTED] = lambda x: x in [1, 3]
        self._scan_patterns = [
            re.compile(r" ALERT:\s+\[(?P<name>.*)\] (?P<file>.*)\s+<")
        ]

    # ==========================================
    #  Antivirus methods (need to be overriden)
    # ==========================================
    def get_version(self):
        """return the version of the antivirus"""
        result = None
        if self.scan_path:
            cmd = self.build_cmd(self.scan_path, "/v")
            retcode, stdout, _ = self.run_cmd(cmd)
            if not retcode:
                # match VDF version is for database
                # matches = re.search(r'VDF Version:\s+'
                #                     r'(?P<version>\d+(\.\d+)+)',
                #                    stdout, re.IGNORECASE)
                # match engine version
                matches = re.search(r'engine set:\s+(?P<version>\d+(\.\d+)+)',
                                    stdout, re.IGNORECASE)
                if matches:
                    result = matches.group('version').strip()
        return result

    def get_database(self):
        """return list of files in the database"""
        search_paths = map(lambda x: "{path}/Avira/scancl".format(path=x),
                                     [os.environ.get('PROGRAMFILES', ''),
                                      os.environ.get('PROGRAMFILES(X86)', '')])
        database_patterns = [
            '*.vdf'
        ]
        results = []
        for pattern in database_patterns:
            result = self.locate(pattern, search_paths, syspath=False)
            results.extend(result)
        return results if results else None

    def get_scan_path(self):
        """return the full path of the scan tool"""
        scan_bin = "scancl.exe"
        scan_paths = map(lambda x: "{path}/Avira/*".format(path=x),
                         [os.environ.get('PROGRAMFILES', ''),
                          os.environ.get('PROGRAMFILES(X86)', '')])
        paths = self.locate(scan_bin, scan_paths)
        return paths[0] if paths else None
