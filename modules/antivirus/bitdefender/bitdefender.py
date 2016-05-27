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
import stat
import tempfile

from ..base import Antivirus

log = logging.getLogger(__name__)


class BitdefenderForUnices(Antivirus):
    _name = "Bitdefender Antivirus Scanner for Unices"

    # ==================================
    #  Constructor and destructor stuff
    # ==================================

    def __init__(self, *args, **kwargs):
        # class super class constructor
        super(BitdefenderForUnices, self).__init__(*args, **kwargs)
        # create a temporary filename
        (fd, self._log_path) = tempfile.mkstemp()
        os.close(fd)
        # scan tool variables
        self._scan_args = (
            "--action=ignore "  # action to take for an infected file
            "--no-list "        # do not display scanned files
            "--log={log}".format(log=self._log_path)
        )
        self._scan_patterns = [
            re.compile(r'(?P<file>[^\s]+)'
                       r'\s+(infected:|suspected:)\s+'
                       r'(?P<name>[^\t]+)', re.IGNORECASE),
        ]

    def __del__(self):
        if os.path.exists(self._log_path):
            os.remove(self._log_path)

    # ==========================================
    #  Antivirus methods (need to be overriden)
    # ==========================================

    def check_scan_results(self, paths, res):
        retcode, stdout, stderr = res[0], None, res[2]
        if self._log_path:
            with open(self._log_path, 'r') as fd:
                stdout = fd.read()
            res = (retcode, stdout, stderr)
        return super(BitdefenderForUnices, self).check_scan_results(paths, res)

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
        # extract folder where are installed definition files
        search_paths = [
            '/opt/BitDefender-scanner/var/lib/scan/Plugins/'
        ]
        database_patterns = [
            '*',
        ]
        results = []
        for pattern in database_patterns:
            result = self.locate(pattern, search_paths, syspath=False)
            results.extend(result)
        return results if results else None

    def get_scan_path(self):
        """return the full path of the scan tool"""
        paths = self.locate("bdscan")
        return paths[0] if paths else None
