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


class FProt(AntivirusUnix):
    name = "F-PROT Antivirus (Linux)"

    # ==================================
    #  Constructor and destructor stuff
    # ==================================

    def __init__(self, *args, **kwargs):
        # class super class constructor
        super().__init__(*args, **kwargs)
        # NOTE: for scan code meanings, do fpscan -x <code>
        self._scan_retcodes[self.ScanResult.INFECTED] = \
            lambda x: (x & 0x3) != 0x0
        self.scan_args = (
            "--report",     # Only report infections.
                            # Never disinfect or delete.
            "--verbose=0",  # Report infections only.
        )
        self.scan_patterns = [
            re.compile('<(?P<name>.+)>\s+(?P<file>.+?)(?:->.+)?$',
                       re.IGNORECASE | re.MULTILINE),
        ]
        self.scan_path = Path("/opt/f-prot/fpscan")
        self.database = [Path("/opt/f-prot/antivir.def"), ]

    # ==========================================
    #  Antivirus methods (need to be overriden)
    # ==========================================

    def get_version(self):
        """return the version of the antivirus"""
        return self._run_and_parse(
            '--version',
            regexp='Engine version:\s+(?P<version>\d+(\.\d+)+)',
            group='version')

    def get_virus_database_version(self):
        """Return the Virus Database version"""
        return self._run_and_parse(
            '--version',
            regexp='Virus signatures:\s+(?P<dbversion>\d+)',
            group='dbversion')
