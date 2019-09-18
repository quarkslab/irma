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

import hashlib
from modules.antivirus.base import Antivirus, AntivirusUnix


class Eicar(AntivirusUnix):
    name = "Eicar Antivirus (Linux)"

    # ==================================
    #  Constructor and destructor stuff
    # ==================================
    def __init__(self, *args, **kwargs):
        # class super class constructor
        super().__init__(*args, **kwargs)
        # scan tool variables
        # WARNING: Don't forget to increment `virus_database_version` value
        # when adding a new hash.
        self.md5list = [
            # eicar.com, eicar.com.txt
            "44d88612fea8a8f36de82e1278abb02f",
            # eicar_com.zip
            "6ce6f415d8475545be5ba114f208b0ff",
            # eicarcom2.zip
            "e4968ef99266df7c9a1f0637d2389dab",
        ]

    # ==========================================
    #  Antivirus methods (need to be overriden)
    # ==========================================
    def get_version(self):
        """return the version of the antivirus"""
        return "1.0.0"


    def get_virus_database_version(self):
        """Return the Virus Database version"""
        return "1"


    def scan(self, paths, env=None):
        md5 = hashlib.md5(paths.read_bytes()).hexdigest()

        if md5 in self.md5list:
            self.scan_results[paths] = "EICAR-STANDARD-ANTIVIRUS-TEST-FILE!"
            return Antivirus.ScanResult.INFECTED

        self.scan_results[paths] = ""
        return Antivirus.ScanResult.CLEAN
