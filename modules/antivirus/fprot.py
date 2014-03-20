import logging, argparse, re, os

from modules.antivirus.base import Antivirus

log = logging.getLogger(__name__)

class FProt(Antivirus):

    ##########################################################################
    # constructor and destructor stuff
    ##########################################################################

    def __init__(self, *args, **kwargs):
        # class super class constructor
        super(FProt, self).__init__(*args, **kwargs)
        # set default antivirus information
        self._name = "F-PROT Antivirus"
        # scan tool variables
        # for scan code meanings, do fpscan -x <code>
        self._scan_retcodes[self.ScanResult.INFECTED] = lambda x: (x and 0xc1) != 0x0
        self._scan_args = (
            "--report " # Only report infections. Never disinfect or delete.
            "--verbose=0 " # Report infections only.
        )
        self._scan_patterns = [
            re.compile(r'\<(?P<name>.*)\>\s+(?P<file>.*)', re.IGNORECASE)
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
        result = None
        if self.scan_path:
            dirname = os.path.dirname(self.scan_path)
            database_path = self.locate('antivir.def', dirname, syspath=False)
            result = database_path
        return result

    def get_scan_path(self):
        """return the full path of the scan tool"""
        paths = self.locate("fpscan", "/usr/local/f-prot/")
        return paths[0] if paths else None
