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
from pathlib import Path

from modules.antivirus.base import AntivirusUnix

log = logging.getLogger(__name__)


class KasperskyFileServer(AntivirusUnix):
    name = "Kaspersky Anti-Virus for File Server(Linux)"

    # ==================================
    #  Constructor and destructor stuff
    # ==================================

    def __init__(self, *args, **kwargs):
        # class super class constructor
        super().__init__(*args, **kwargs)
        self.scan_args = ("--scan-file", )
        self.scan_patterns = [
            re.compile("(Threats found:)\s*[1-9][0-9]*"),
        ]
        # Kaspersky does not use return value as infection indicator.
        # Cf. self.check_scan_results()
        self._scan_retcodes[self.ScanResult.INFECTED] = lambda x: x in [0]
        self.scan_path = Path("/opt/kaspersky/kav4fs/bin/kav4fs-control")

    # ==========================================
    #  Antivirus methods (need to be overriden)
    # ==========================================

    def get_version(self):
        """return the version of the antivirus"""
        return self._run_and_parse(
            '-S', '--app-info',
            regexp='(?P<version>\d+([.-]\d+)+)',
            group='version')

    def get_virus_database_version(self):
        """Return the Virus Database version"""
        return self._run_and_parse(
            '--get-stat', 'Update',
            regexp='(?P<dbversion>\d+([.-]\d+)+)',
            group='dbversion')

    def get_database(self):
        """return list of files in the database"""
        search_paths = [Path('/var/opt/kaspersky/kav4fs/update/avbases'), ]
        return self.locate('*.kdc', search_paths, syspath=False)

    def check_scan_results(self, paths, results):
        # Kaspersky does not differenciate an infected scan from a clean scan
        # on its return code, thus this method need to be specialized
        log.debug("scan results for {0}: {1}".format(paths, results))
        self.scan_results[paths] = None
        retcode, stdout, stderr = results
        if self._scan_retcodes[self.ScanResult.ERROR](retcode):
            self.scan_results[paths] = stderr or stdout
            log.error("command line returned {}: {}".format(
                retcode, (stdout, stderr)))
            return self.ScanResult.ERROR

        if not stdout:
            return self.ScanResult.ERROR

        for pattern in self.scan_patterns:
            if pattern.search(stdout):
                self.scan_results[paths] = "Infected"
                return self.ScanResult.INFECTED
        # Did not find any threat
        return self.ScanResult.CLEAN
