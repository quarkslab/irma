import logging, argparse, re

from lib.common.hash import sha256sum
from modules.antivirus.base import Antivirus

log = logging.getLogger(__name__)

class McAfeeVSCL(Antivirus):

    ##########################################################################
    # constructor and destructor stuff
    ##########################################################################

    def __init__(self, *args, **kwargs):
        # class super class constructor
        super(McAfeeVSCL, self).__init__(*args, **kwargs)
        # set default antivirus information
        self._name = "McAfee VirusScan Command Line scanner"
        # scan tool variables
        self._scan_args = (
            "--ASCII " # display filenames as ASCII text
            "--ANALYZE " # turn on heuristic analysis for programs and macros
            "--MANALYZE " # turn on macro heuristics
            "--MACRO-HEURISTICS " # turn on macro heuristics
            "--RECURSIVE " # examine any subdirectories in addition to the specified target directory.
            "--UNZIP " # scan inside archive files
        )
        self._scan_patterns = [
            re.compile(r'(?P<file>.*) \.\.\. Found the (?P<name>.*) [a-z]+ \!\!', re.IGNORECASE),
            re.compile(r'(?P<file>.*) \.\.\. Found [a-z]+ or variant (?P<name>.*) \!\!', re.IGNORECASE),
        ]

    ##########################################################################
    # antivirus methods (need to be overriden)
    ##########################################################################

    def get_version(self):
        """return the version of the antivirus"""
        result = None
        if self.scan_path:
            cmd = self.build_cmd(self.scan_path, '--version')
            retcode, stdout, stderr = self.run_cmd(cmd)
            if not retcode:
                matches = re.search(r'(?P<version>\d+(\.\d+)+)', stdout, re.IGNORECASE)
                if matches:
                    result = matches.group('version').strip()
        return result

    def get_database(self):
        """return list of files in the database"""
        search_paths = [
            '/usr/local/uvscan', # default location in debian
        ]
        database_patterns = [
            'avvscan.dat', # data file for virus scanning
            'avvnames.dat', # data file for virus names
            'avvclean.dat', # data file for virus cleaning
        ]
        results = []
        for pattern in database_patterns:
            result = self.locate(pattern, search_paths)
            results.extend(result)
        return results if results else None

    def get_scan_path(self):
        """return the full path of the scan tool"""
        paths = self.locate("uvscan")
        return paths[0] if paths else None
