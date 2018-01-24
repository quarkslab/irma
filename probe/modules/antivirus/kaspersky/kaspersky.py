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


class KasperskyFileServer(Antivirus):
    _name = "Kaspersky Anti-Virus for File Server (Linux)"

    # ==================================
    #  Constructor and destructor stuff
    # ==================================

    def __init__(self, *args, **kwargs):
        # class super class constructor
        super(KasperskyFileServer, self).__init__(*args, **kwargs)
        self._scan_args = ("--scan-file")
        self._scan_patterns = [
            re.compile(b"(Threats found:)\s*[1-9][0-9]*"),
            ]
        # Kaspersky does not use return value as infection indicator
        self._scan_retcodes[self.ScanResult.INFECTED] = lambda x: x in [0]

    # ==========================================
    #  Antivirus methods (need to be overriden)
    # ==========================================

    def get_version(self):
        """return the version of the antivirus"""
        result = None
        if self.scan_path:
            cmd = self.build_cmd(self.scan_path, '-S --app-info')
            retcode, stdout, _ = self.run_cmd(cmd)
            if not retcode:
                matches = re.search(b'(?P<version>\d+([.-]\d+)+)',
                                    stdout,
                                    re.IGNORECASE)
                if matches:
                    result = matches.group('version').strip()
        return result

    def get_database(self):
        """return list of files in the database"""
        search_paths = ['/var/opt/kaspersky/kav4fs/update/avbases']
        database_patterns = ['*.kdc']
        results = []
        for pattern in database_patterns:
            result = self.locate(pattern, search_paths, syspath=False)
            results.extend(result)
        return results if results else None

    def get_scan_path(self):
        """return the full path of the scan tool"""
        paths = self.locate("kav4fs-control", "/opt/kaspersky/kav4fs/bin/")
        return paths[0] if paths else None

    def scan(self, paths):
        # override scan as comodo uses only absolute paths, we need to convert
        # provided paths to absolute paths first
        paths = os.path.abspath(paths)
        return super(KasperskyFileServer, self).scan(paths)

    def check_scan_results(self, paths, results):
        log.debug("scan results for {0}: {1}".format(paths, results))
        self._scan_results[paths] = None
        retcode, stdout, stderr = results
        if self._scan_retcodes[self.ScanResult.ERROR](retcode):
            retcode = self.ScanResult.ERROR
            self._scan_results[paths] = stderr if stderr else stdout
            log.error("command line returned {0}".format(retcode) +
                      ": {0}".format((stdout, stderr)))
        else:
            if stdout:
                infected = False
                for line in stdout.splitlines():
                    for pattern in self.scan_patterns:
                        if pattern.match(line):
                            retcode = self.ScanResult.INFECTED
                            infected = True
                            self._scan_results[paths] = "Infected"
                            break
                    if infected:
                        break
                if not infected:
                    retcode = self.ScanResult.CLEAN
        return retcode
