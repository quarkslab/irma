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


class ASquaredCmd(Antivirus):
    _name = "Emsisoft Commandline Scanner"

    # ==================================
    #  Constructor and destructor stuff
    # ==================================

    def __init__(self, *args, **kwargs):
        # class super class constructor
        super(ASquaredCmd, self).__init__(*args, **kwargs)
        # scan tool variables
        self._scan_args = (
            "/h "
            "/r "
            "/a "
            "/n "
            "/f "
        )
        # scan tool variables
        self._scan_patterns = [
            re.compile(r'\\\s+(?P<file>.*)\s+detected:\s+(?P<name>.*[^\s]+)')
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
            if not retcode:
                matches = re.search(r'(?P<version>\d+(\.\d+)+)',
                                    stdout, re.IGNORECASE)
                if matches:
                    result = matches.group('version').strip()
        return result

    def get_database(self):
        """return list of files in the database"""
        # TODO: make locate() to be reccursive, and to extend selected folders
        pf_path = [os.environ.get('PROGRAMFILES', ''),
                   os.environ.get('PROGRAMFILES(X86)', '')]
        search_paths = map(lambda (x, y):
                           "{path}/Emsisoft/a2cmd/Signatures/{folder}"
                           "".format(path=x, folder=y),
                           ((x, y) for x in pf_path for y in ['', 'BD']))
        results = self.locate('*', search_paths, syspath=False)
        return results if results else None

    def get_scan_path(self):
        """return the full path of the scan tool"""
        scan_bin = "a2cmd.exe"
        scan_paths = map(lambda x: "{path}/Emsisoft/a2cmd/".format(path=x),
                         [os.environ.get('PROGRAMFILES', ''),
                          os.environ.get('PROGRAMFILES(X86)', '')])
        paths = self.locate(scan_bin, scan_paths)
        return paths[0] if paths else None
