import logging, argparse, re

from modules.antivirus.base import Antivirus

log = logging.getLogger(__name__)

class Clam(Antivirus):

    ##########################################################################
    # constructor and destructor stuff
    ##########################################################################

    def __init__(self, *args, **kwargs):
        # class super class constructor
        super(Clam, self).__init__(*args, **kwargs)
        # set default antivirus information
        self._name = "Clam AntiVirus Scanner"
        # scan tool variables
        self._scan_args = (
            "--infected "   # only print infected files
            "--fdpass "     # avoid file access problem as clamdameon is runned by clamav user
            "--no-summary " # disable summary at the end of scanning
            "--stdout "     # do not write to stderr
        )
        self._scan_patterns = [
            re.compile(r'(?P<file>.*): (?P<name>[^\s]+) FOUND', re.IGNORECASE)
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
        # NOTE: we can use clamconf to get database location, but it is not
        # always installed by default. Instead, hardcode some common paths and
        # locate files using predefined patterns
        search_paths = [
            '/var/lib/clamav', # default location in debian
        ]
        database_patterns = [
            'main.cvd',
            'daily.c[lv]d', # *.cld on debian and on *.cvd on clamav website
            'bytecode.c[lv]d', # *.cld on debian and on *.cvd on clamav website
            'safebrowsing.c[lv]d', # *.cld on debian and on *.cvd on clamav website
            '*.hdb', # clamav hash database
            '*.mdb', # clamav MD5, PE-section based
            '*.ndb', # clamav extended signature format
            '*.ldb', # clamav logical signatures
        ]
        results = []
        for pattern in database_patterns:
            result = self.locate(pattern, search_paths, syspath=False)
            results.extend(result)
        return results if results else None

    def get_scan_path(self):
        """return the full path of the scan tool"""
        paths = self.locate("clamdscan")
        return paths[0] if paths else None
