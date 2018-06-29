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
from datetime import datetime
from pathlib import Path

from modules.antivirus.base import AntivirusUnix

log = logging.getLogger(__name__)


class ComodoCAVL(AntivirusUnix):
    name = "Comodo Antivirus (Linux)"

    # ==================================
    #  Constructor and destructor stuff
    # ==================================

    def __init__(self, *args, **kwargs):
        # class super class constructor
        super().__init__(*args, **kwargs)
        # Comodo does not use return value as infection indicator. Distinction
        # between INFECTED and CLEAN will be done in the 'false positive
        # handler' of Antivirus.scan()
        self._scan_retcodes[self.ScanResult.INFECTED] = lambda x: x in [0]
        # scan tool variables
        self.scan_args = (
            "-v",  # verbose mode, display more detailed output
            "-s",  # scan a file or directory
        )
        self.scan_patterns = [
            re.compile('(?P<file>.*) ---> Found .*,' +
                       ' Malware Name is (?P<name>.*)', re.IGNORECASE),
        ]
        self.scan_path = Path("/opt/COMODO/cmdscan")

    # ==========================================
    #  Antivirus methods (need to be overriden)
    # ==========================================

    def get_version(self):
        """return the version of the antivirus"""
        return Path('/opt/COMODO/cavver.dat').read_text()

    def get_database(self):
        """return list of files in the database"""
        search_paths = [Path('/opt/COMODO/scanners/'), ]
        return self.locate('*.cav', search_paths, syspath=False)

    def get_virus_database_version(self):
        """Return the Virus Database version"""
        d = Path("/opt/COMODO/scanners/bases.cav").stat().st_mtime
        return datetime.fromtimestamp(d).strftime('%Y-%m-%d')
