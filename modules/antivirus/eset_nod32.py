import logging, argparse, re

from lib.common.hash import sha256sum
from modules.antivirus.base import Antivirus

log = logging.getLogger(__name__)

class EsetNod32(Antivirus):

    ##########################################################################
    # constructor and destructor stuff
    ##########################################################################

    def __init__(self, *args, **kwargs):
        # class super class constructor
        super(EsetNod32, self).__init__(*args, **kwargs)
        # set default antivirus information
        self._name = "ESET NOD32 Antivirus Business Edition for Linux Desktop"
        # Modify retun codes (see --help for details)
        self._scan_retcodes[self.ScanResult.INFECTED] = lambda x: x in [1, 50]
        # scan tool variables
        self._scan_args = (
            "--clean-mode=NONE " # do not remove infected files
            "--no-log-all" # do not log clean files
        )
        self._scan_patterns = [
            re.compile(r'name="(?P<file>.*)", threat="(?P<name>.*), action=.*', re.IGNORECASE|re.MULTILINE)
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
            '/var/opt/eset/esets/lib/', 
        ]
        database_patterns = [
            '*.dat', # determined using strace on linux
        ]
        results = []
        for pattern in database_patterns:
            result = self.locate(pattern, search_paths)
            results.extend(result)
        return results if results else None

    def get_scan_path(self):
        """return the full path of the scan tool"""
        paths = self.locate("esets_scan", "/opt/eset/esets/sbin/")
        return paths[0] if paths else None
