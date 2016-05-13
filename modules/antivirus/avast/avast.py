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

from ..base import Antivirus

log = logging.getLogger(__name__)


class AvastCoreSecurity(Antivirus):
    _name = "Avast Core Security"

    # ==================================
    #  Constructor and destructor stuff
    # ==================================

    def __init__(self, *args, **kwargs):
        # class super class constructor
        super(AvastCoreSecurity, self).__init__(*args, **kwargs)
        # scan tool variables
        self._scan_args = (
            "-b "  # Report decompression bombs as infections
            "-f "  # Scan full files
            "-u "  # Report potentionally unwanted programs (PUP)
        )
        self._scan_patterns = [
            re.compile(r'(?P<file>[^ \t]+)\t+(?P<name>[^\t]+)', re.IGNORECASE)
        ]

    # ==========================================
    #  Antivirus methods (need to be overriden)
    # ==========================================

    def scan(self, paths):
        # NOTE: assuming that avast is in the group of the user that executes
        # the probe_app, do chmod g+r to let avast daemon read the file.
        # Permission changes can be done also in the FTP handler, but it will
        # also grant unnecessary permissions to other probes.
        if isinstance(paths, list):
            abspaths = map(os.path.abspath, paths)
            for abspath in abspaths:
                st = os.stat(abspath)
                os.chmod(abspath, st.st_mode | stat.S_IRGRP)
        else:
            abspath = os.path.abspath(paths)
            st = os.stat(abspath)
            os.chmod(abspath, st.st_mode | stat.S_IRGRP)
        # Call super class method
        return super(AvastCoreSecurity, self).scan(paths)

    def get_version(self):
        """return the version of the antivirus"""
        result = None
        if self.scan_path:
            cmd = self.build_cmd(self.scan_path, '-v')
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
        avast_path = '/var/lib/avast/'
        db_version = None
        try:
            vps_lat_path = os.path.join(avast_path, 'Setup/filedir/vps.lat')
            vps_lat_path = os.path.normpath(vps_lat_path)
            with open(vps_lat_path, 'r') as fd:
                db_version = fd.read().strip()
        except:
            return None

        # NOTE: the structure/location of the update folders are documented in
        # the /var/lib/avast/Setup/avast.setup script.
        search_paths = map(lambda x:
                           '{avast_path}/defs/{db_version}/'
                           ''.format(avast_path=avast_path, db_version=x),
                           [db_version, '%s_stream' % db_version])
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
        paths = self.locate("scan")
        return paths[0] if paths else None
