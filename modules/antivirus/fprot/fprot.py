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


class FProt(Antivirus):

    # ==================================
    #  Constructor and destructor stuff
    # ==================================

    def __init__(self, *args, **kwargs):
        # class super class constructor
        super(FProt, self).__init__(*args, **kwargs)
        # set default antivirus information
        self._name = "F-PROT Antivirus"
        # scan tool variables
        # for scan code meanings, do fpscan -x <code>
        code_infected = self.ScanResult.INFECTED
        self._scan_retcodes[code_infected] = lambda x: (x and 0xc1) != 0x0
        self._scan_args = (
            "--report "     # Only report infections.
                            # Never disinfect or delete.
            "--verbose=0 "  # Report infections only.
        )
        self._scan_patterns = [
            re.compile(r'\<(?P<name>.*)\>\s+(?P<file>.*)', re.IGNORECASE)
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
        result = None
        if self.scan_path:
            dirname = os.path.dirname(self.scan_path)
            database_path = self.locate('antivir.def', dirname, syspath=False)
            result = database_path
        return result

    def get_scan_path(self):
        """return the full path of the scan tool"""
        paths = self.locate("fpscan", "/usr/local/f-prot/")
        return paths[0] if paths else None
