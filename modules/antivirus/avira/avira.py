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
        self._scan_args = (
            "/z",
            "/a"
        )
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
            cmd = self.build_cmd(self.scan_path)
            retcode, stdout, stderr = self.run_cmd(cmd)
            # if not retcode:
            # match VDF version is for database
            # matches = re.search(r'VDF Version:\s+'
            #                     r'(?P<version>\d+(\.\d+)+)',
            #                     stdout, re.IGNORECASE)
            # Match engine version
            matches = re.search(r'engine set:\s+(?P<version>\d+(\.\d+)+)',
                                stdout,
                                re.IGNORECASE)
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
