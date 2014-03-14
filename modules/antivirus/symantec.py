import logging, argparse, re, os, time, glob

from datetime import date
from modules.antivirus.base import Antivirus

log = logging.getLogger(__name__)

class Symantec(Antivirus):

    ##########################################################################
    # constructor and destructor stuff
    ##########################################################################

    def __init__(self, *args, **kwargs):
        # class super class constructor
        super(Symantec, self).__init__(*args, **kwargs)
        # set default antivirus information
        self._name = "Symantec Anti-Virus"
        # scan tool variables
        self._scan_args = (
            "/ScanFile " # scan command
        )
        self._scan_patterns = [
            re.compile(r"([^,]*,){6}(?P<name>[^,]*),(?P<file>[^,]*).*", re.IGNORECASE)
        ]
        self._pdata_path = glob.glob(os.path.normcase('\\'.join([os.environ.get('PROGRAMDATA', ''), r"Symantec\Symantec Endpoint Protection\*.*"])))
        self._pdata_path = self._pdata_path.pop() if self._pdata_path else None

    ##########################################################################
    # antivirus methods (need to be overriden)
    ##########################################################################

    def get_version(self):
        """return the version of the antivirus"""
        result = None
        if self._pdata_path:
            matches = re.search(r'(?P<version>\d+(\.\d+)+)', self._pdata_path, re.IGNORECASE)
            if matches:
                result = matches.group('version').strip()
        return result

    def get_database(self):
        """return list of files in the database"""
        return None

    def get_scan_path(self):
        """return the full path of the scan tool"""
        scan_bin = "DoScan.exe"
        scan_paths = map(lambda x: "{path}/Symantec/*".format(path=x), [os.environ.get('PROGRAMFILES', ''), os.environ.get('PROGRAMFILES(X86)', '')])
        paths = self.locate(scan_bin, scan_paths)
        return paths[0] if paths else None

    ##########################################################################
    # specific scan method
    ##########################################################################

    # TODO: implement heuristic levels
    def scan(self, paths, heuristic=None):
        # get log path and modification time
        self._log_path = os.path.normcase('\\'.join([self._pdata_path, "Data\Logs\AV", date.today().strftime('%m%d%Y.Log')]))
        self._log_path = glob.glob(self._log_path)
        self._log_path = self._log_path[0] if self._log_path else None
        self._last_log_time = time.time()
        if self._log_path:
            self._last_log_time = os.path.getmtime(self._log_path)
        return super(Symantec, self).scan(paths, heuristic)

    def check_scan_results(self, paths, results):
        retcode, stdout, stderr = results[0], None, results[2]
        if self._log_path:
            # wait for log to be updated
            mtime = os.path.getmtime(self._log_path) if self._log_path else time.time()
            if not self._last_log_time < mtime:
                time.sleep(.5)
            # look for the line corresponding to this filename
            with open(self._log_path, 'r') as fd:
                for line in reversed(fd.readlines()):
                    if paths in line:
                        stdout = line
	    # force scan_result to consider it infected
	    retcode = 1 if stdout else 0
            results = (retcode, stdout, stderr)
        return super(Symantec, self).check_scan_results(paths, results)
