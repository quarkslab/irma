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
import tempfile
from pathlib import Path

from modules.antivirus.base import AntivirusUnix

log = logging.getLogger(__name__)


class BitdefenderForUnices(AntivirusUnix):
    name = "Bitdefender Antivirus Scanner (Linux)"

    # ==================================
    #  Constructor and destructor stuff
    # ==================================

    def __init__(self, *args, **kwargs):
        # class super class constructor
        super().__init__(*args, **kwargs)
        # create a temporary filename
        fd, self._log_path = tempfile.mkstemp()
        self._log_path = Path(self._log_path)
        os.close(fd)

        # scan tool variables
        self.scan_args = (
            "--action=ignore",  # action to take for an infected file
            "--no-list",        # do not display scanned files
            "--log={log}".format(log=self._log_path)
        )
        self.scan_patterns = [
            re.compile('(?P<file>\S+)\s+(infected:|suspected:)\s+'
                       '(?P<name>.+?)$', re.IGNORECASE | re.MULTILINE),
        ]

    def __del__(self):
        if hasattr(self, '_log_path') and self._log_path.exists():
            self._log_path.unlink()

    # ==========================================
    #  Antivirus methods (need to be overriden)
    # ==========================================

    def check_scan_results(self, paths, res):
        retcode, _, stderr = res
        stdout = self._log_path.read_text()
        return super().check_scan_results(paths, (retcode, stdout, stderr))

    def get_version(self):
        """return the version of the antivirus"""
        return self._run_and_parse(
            '--version',
            regexp='(?P<version>\d+(\.\d+)+)',
            group='version')

    def get_database(self):
        """return list of files in the database"""
        # extract folder where are installed definition files
        search_paths = [
            Path('/opt/BitDefender-scanner/var/lib/scan/Plugins/'),
        ]
        return self.locate('*', search_paths, syspath=False)

    def get_scan_path(self):
        """return the full path of the scan tool"""
        return self.locate_one("bdscan")

    def get_virus_database_version(self):
        """Return the Virus Database version"""
        self._run_and_parse(
            '--info',
            regexp='Engine signatures: (?P<dbversion>\d+)',
            group='dbversion')
