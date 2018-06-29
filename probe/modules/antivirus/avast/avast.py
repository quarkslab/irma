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
import stat

from modules.antivirus.base import AntivirusUnix

log = logging.getLogger(__name__)


class AvastCoreSecurity(AntivirusUnix):
    name = "Avast Core Security (Linux)"

    # ==================================
    #  Constructor and destructor stuff
    # ==================================

    def __init__(self, *args, **kwargs):
        # class super class constructor
        super().__init__(*args, **kwargs)
        # scan tool variables
        self.scan_args = (
            "-b",  # Report decompression bombs as infections
            "-f",  # Scan full files
            "-u",  # Report potentionally unwanted programs (PUP)
        )
        self.scan_patterns = [
            re.compile('(?P<file>\S+)\t+(?P<name>.+?)$',
                       re.IGNORECASE | re.MULTILINE),
        ]

    # ==========================================
    #  Antivirus methods (need to be overriden)
    # ==========================================

    def scan(self, path):
        # NOTE: assuming that avast is in the group of the user that executes
        # the probe_app, do chmod g+r to let avast daemon read the file.
        # Permission changes can be done also in the FTP handler, but it will
        # also grant unnecessary permissions to other probes.

        # TODO: enable multiple paths (cf. Antivirus.scan())
        mode = path.stat().st_mode
        path.chmod(mode | stat.S_IRGRP)
        # Call super class method
        return super().scan(path)

    def get_version(self):
        """return the version of the antivirus"""
        return self._run_and_parse(
            '-v',
            regexp='(?P<version>\d+(\.\d+)+)',
            group='version')

    def get_database(self):
        """return list of files in the database"""
        avastdir = Path('/var/lib/avast')

        # NOTE: the structure/location of the update folders are documented in
        # the /var/lib/avast/Setup/avast.setup script.
        search_paths = [
            avastdir / 'defs' / self.virus_database_version,
            avastdir / 'defs' / (self.virus_database_version + '_stream'),
        ]
        return self.locate('*', search_paths, syspath=False)

    def get_scan_path(self):
        """return the full path of the scan tool"""
        return self.locate_one("scan")

    def get_virus_database_version(self):
        """return the version of the Virus Database of the Antivirus"""
        avastdir = Path('/var/lib/avast')
        db_file = avastdir / 'Setup/filedir/vps.lat'

        return db_file.read_text().strip()
