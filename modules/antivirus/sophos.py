import logging
import re
import os
import tempfile
import time

from modules.antivirus.base import Antivirus

log = logging.getLogger(__name__)


class Sophos(Antivirus):

    # ==================================
    #  Constructor and destructor stuff
    # ==================================

    def __init__(self, *args, **kwargs):
        # class super class constructor
        super(Sophos, self).__init__(*args, **kwargs)
        # set default antivirus information
        self._name = "Sophos Anti-Virus"
        # scan tool variables
        self._scan_args = (
            "-archive "  # scan inside archives
            "-cab " # scan microsoft cab file
            "-loopback " # scan loopback-type file
            "-tnef " # scan tnet file
            "-mime " # scan file encoded with mime format
            "-oe " # scan microsoft outlook
            "-pua " # scan file encoded with mime format
            "-ss "  # only print errors or found viruses
            "-nc "  # do not ask remove confirmation when infected
            "-nb "  # no bell sound
        )
        code_infected = self.ScanResult.INFECTED
        # NOTE: on windows, 0 can be returned even if the file is infected
        self._scan_retcodes[code_infected] = lambda x: x in [0, 1, 2, 3]
        self._scan_patterns = [
            re.compile(r">>> Virus '(?P<name>.+)' found in file (?P<file>.+)",
                       re.IGNORECASE)
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
                matches = re.search(r'(?P<version>\d+(\.\d+)+)',
                                    stdout,
                                    re.IGNORECASE)
                if matches:
                    result = matches.group('version').strip()
        return result

    def get_database(self):
        """return list of files in the database"""
        # NOTE: we can use clamconf to get database location, but it is not
        # always installed by default. Instead, hardcode some common paths and
        # locate files using predefined patterns
        if self._is_windows:
            search_paths = map(lambda x: "{path}/Sophos/*".format(path=x),
                               [os.environ.get('PROGRAMFILES', ''),
                                os.environ.get('PROGRAMFILES(X86)', '')])
        else:
            search_paths = [
                '/opt/sophos-av/lib/sav',  # default location in debian
            ]
        database_patterns = [
            '*.dat',
            'vdl??.vdb',
            'sus??.vdb',
            '*.ide',
        ]
        results = []
        for pattern in database_patterns:
            result = self.locate(pattern, search_paths, syspath=False)
            results.extend(result)
        return results if results else None

    def get_scan_path(self):
        """return the full path of the scan tool"""
        if self._is_windows:
            scan_bin = "sav32cli.exe"
            scan_paths = map(lambda x:
                             "{path}/Sophos".format(path=x),
                             [os.environ.get('PROGRAMFILES', ''),
                              os.environ.get('PROGRAMFILES(X86)', '')])
        else:
            scan_bin = "savscan"
            scan_paths = "/opt/sophos-av"
        paths = self.locate(scan_bin, scan_paths)
        return paths[0] if paths else None

    def scan(self, paths, heuristic=None):
        # quirk to force lang in linux
        if not self._is_windows:
            os.environ['LANG'] = "C"
        return super(Sophos, self).scan(paths, heuristic)
