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
import stat
import tempfile

from ..base import Antivirus

log = logging.getLogger(__name__)


class FSecure(Antivirus):

    # ==================================
    #  Constructor and destructor stuff
    # ==================================

    def __init__(self, *args, **kwargs):
        # class super class constructor
        super(FSecure, self).__init__(*args, **kwargs)
        # set default antivirus information
        self._name = "FSecure Antivirus for Linux Desktop"
        # scan tool variables
        self._scan_args = (
            "--allfiles=yes ",
            "--scanexecutables=yes ",
            "--archive=yes ",
            "--mime=yes ",
            #"--riskware=yes ",
            "--virus-action1=report ",
            #"--riskware-action1=report ",
            "--suspected-action1=report ",
            "--virus-action2=none ",
            #"--riskware-action2=none ",
            "--suspected-action2=none ",
            "--auto=yes ",
            "--list=no ",
        )
        # see man zavcli for return codes
        self._scan_retcodes[self.ScanResult.INFECTED] = lambda x: x in [3]
        self._scan_retcodes[self.ScanResult.ERROR] = lambda x: x in [1, 3, 9]
        self._scan_patterns = [
            re.compile(r'(?P<file>.*)'
                       r':\s+(Infected|Suspected):\s+'
                       r'(?P<name>.*)', re.IGNORECASE),
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
                matches = re.search(r'(?P<version>\d+([.-]\d+)+)',
                                    stdout,
                                    re.IGNORECASE)
                if matches:
                    result = matches.group('version').strip()
        return result

    def get_database(self):
        """return list of files in the database"""
        # extract folder where are installed definition files
        drweb_path = "/var/opt/drweb.com/"
        #search_paths = map(lambda x:
        #                   '{drweb_path}/lib/{folder}/'
        #                   ''.format(drweb_path=drweb_path, folder=x),
        #                   ['bases', 'dws'])
        #database_patterns = [
        #    'timestamp*',
        #    '*.drl',
        #    '*.dws',
        #    '*.vdb',
        #]
        results = []
        #for pattern in database_patterns:
        #    result = self.locate(pattern, search_paths, syspath=False)
        #    results.extend(result)
        return results if results else None

    def get_scan_path(self):
        """return the full path of the scan tool"""
        paths = self.locate("fsav")
        return paths[0] if paths else None
