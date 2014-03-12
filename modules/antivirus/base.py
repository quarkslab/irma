import logging, re, os, sys, glob

from lib.common.hash import sha256sum
from subprocess import Popen, PIPE


log = logging.getLogger(__name__)

class Antivirus(object):
    """Antivirus Base Class"""

    ##########################################################################
    # constants
    ##########################################################################

    class ScanResult:
        CLEAN    = 0
        INFECTED = 1
        ERROR    = 2

    class ScanHeuristic:
        NONE     = 0
        LOW      = 1
        MEDIUM   = 2
        HIGH     = 3

    ##########################################################################
    # constructor and destructor stuff
    ##########################################################################

    def __init__(self, *args, **kwargs):
        # set default antivirus information
        self._name = None
        self._version = None
        self._database = None
        # scan tool variables
        self._scan_path = None
        self._scan_args = []
        self._scan_retcodes = {
            self.ScanResult.CLEAN    : lambda x: x in [0],
            self.ScanResult.INFECTED : lambda x: x in [1],
            self.ScanResult.ERROR    : lambda x: not self._scan_retcodes[self.ScanResult.CLEAN](x) and not self._scan_retcodes[self.ScanResult.INFECTED](x),
        }
        # scan options
        # TODO: implement heuristics levels
        self._scan_heuristic = self.ScanHeuristic.NONE
        # scan pattern-matching
        self._scan_patterns = []
        # initialize result as an empty dictionary
        self._scan_results = dict()
        self._is_windows = sys.platform.startswith('win')

    ##########################################################################
    # antivirus methods
    ##########################################################################

    def ready(self):
        result = False
        if self.scan_path and os.path.exists(self.scan_path):
            if os.path.isfile(self.scan_path):
                result = True
        return result

    # TODO: enable multiple paths
    # TODO: enable heuristics levels
    def scan_cmd(self, paths, heuristic=None):
        cmd = self.scan_path
        args = self.scan_args
        return self.build_cmd(cmd, args, paths)

    # TODO: implement heuristic levels
    def scan(self, paths, heuristic=None):
        # check if ready
        if not self.ready():
            raise RuntimeError("{0} not ready".format(type(self).__name__))
        # check if patterns are set
        if not self.scan_patterns:
            raise ValueError("scan_patterns not defined")
        # build the command to be executed and run it
        if isinstance(paths, list):
            paths = map(os.path.abspath, paths)
        else:
            paths = os.path.abspath(paths)
        cmd = self.scan_cmd(paths, heuristic)
        results = self.run_cmd(cmd)
        log.debug("Executed command line: {0}, results {1}".format(cmd, results))
        return self.check_scan_results(paths, results)

    ##########################################################################
    # internal helpers
    ##########################################################################

    @staticmethod
    def build_cmd(cmd, *args):
        cmd = [cmd]
        for param in args:
            if isinstance(param, (tuple, list)):
                cmd.extend(param)
            else:
                cmd.append(param)
        return " ".join(cmd)

    @staticmethod
    def run_cmd(cmd):
        # remove whitespace with re.sub, then split()
        re.sub(r'\s+', ' ', cmd)
        cmdarray = cmd.split()
        # execute command with popen, clean up outputs
        pd = Popen(cmdarray, stdout=PIPE, stderr=PIPE)
        stdout, stderr = map(lambda x: x.strip() if x.strip() else None, pd.communicate())
        retcode = pd.returncode
        # return tuple (retcode, out, err)
        return (retcode, stdout, stderr)

    @staticmethod
    def locate(file, paths=None):
        # always add system path to search paths
        search_paths = os.environ.get('PATH', None)
        search_paths = search_paths.split(os.pathsep) if search_paths else []
        # append additionnal paths
        if paths:
            paths = [paths] if isinstance(paths, basestring) else list(paths)
            search_paths.extend(paths)
        # search path using glob to support meta-characters
        results = []
        search_paths = map(lambda p: os.path.join(p, file), search_paths)
        for path in search_paths:
            results.extend(glob.glob(path))
        # convert to absolute paths
        return map(os.path.abspath, results) if results else []

    def check_scan_results(self, paths, results):
        log.debug("scan results for {0}: {1}".format(paths, results))
        # create clean entries for all paths
        # TODO: add more info
        self.scan_results[paths] = None
        # unpack results and uniformize return code
        retcode, stdout, stderr = results
        if self._scan_retcodes[self.ScanResult.CLEAN](retcode):
            retcode = self.ScanResult.CLEAN
        elif self._scan_retcodes[self.ScanResult.INFECTED](retcode):
            retcode = self.ScanResult.INFECTED
        elif self._scan_retcodes[self.ScanResult.ERROR](retcode):
            retcode = self.ScanResult.ERROR
            log.error("command line returned {0}: {1}".format(retcode, (stdout, stderr)))
        else:
            raise RuntimeError("unhandled return code {0} in class {1}: {2}".format(retcode, type(self).__name__, results))
        # handle infected and error error codes
        if retcode in [self.ScanResult.INFECTED, self.ScanResult.ERROR]:
            if stdout:
                for pattern in self.scan_patterns:
                    matches = pattern.finditer(stdout)
                    for match in matches:
                        self.scan_results[match.group('file')] = match.group('name')
        return retcode

    ##########################################################################
    # getters (for RO variable, for late resolution and value uniformisation)
    ##########################################################################

    @property
    def name(self):
        if not self._name:
            self._name = self.get_name()
        return self._name

    @property
    def version(self):
        if not self._version:
            self._version = self.get_version()
        return self._version

    @property
    def database(self):
        if not self._database:
            self._database = self.get_database()
        return self._database

    @property
    def scan_path(self):
        if not self._scan_path:
            self._scan_path = self.get_scan_path()
        return self._scan_path

    @property
    def scan_args(self):
        if not self._scan_args:
            self._scan_args = str(self.get_scan_args())
        return self._scan_args

    @property
    def scan_patterns(self):
        if isinstance(self._scan_patterns, (tuple, list)):
            results = self._scan_patterns
        else:
            results = list(self._scan_patterns)
        return results

    @property
    def scan_results(self):
        return self._scan_results

    ##########################################################################
    # antivirus methods (need to be overriden)
    ##########################################################################

    def get_name(self):
        """return the name of the antivirus"""
        return None

    def get_version(self):
        """return the version of the antivirus"""
        return None

    def get_database(self):
        """return list of files in the database"""
        return None

    def get_scan_path(self):
        """return the full path of the scan tool"""
        return None

    def get_scan_args(self):
        """return the scan arguments"""
        return None

##############################################################################
# CLI for debug purposes
##############################################################################

if __name__ == '__main__':

    ##########################################################################
    # imports
    ##########################################################################

    import argparse
    from modules.antivirus.clam        import Clam
    from modules.antivirus.comodo_cavl import ComodoCAVL
    from modules.antivirus.eset_nod32  import EsetNod32
    from modules.antivirus.fprot       import FProt
    from modules.antivirus.mcafee_vscl import McAfeeVSCL
    from modules.antivirus.sophos      import Sophos
    from modules.antivirus.kaspersky   import Kaspersky

    ##########################################################################
    # helpers
    ##########################################################################

    antivirus_mapping = {
        'clam'       : Clam,
        'comodo_cavl': ComodoCAVL,
        'eset_nod32' : EsetNod32,
        'fprot'      : FProt,
        'mcafee_vscl': McAfeeVSCL,
        'sophos'     : Sophos,
        'kaspersky'  : Kaspersky,
    }

    def antivirus_info(**kwargs):
        antivirus = antivirus_mapping[kwargs['antivirus']]()
        # build output string
        result  = "name    : {0}\n".format(antivirus.name)
        result += "version : {0}\n".format(antivirus.version)
        result += "database: \n"
        if antivirus.database:
            for file in antivirus.database:
                result += "    {0} (sha256 = {1})\n".format(file, sha256sum(file))
        print(result)

    def antivirus_scan(**kwargs):
        antivirus = antivirus_mapping[kwargs['antivirus']]()
        for filename in kwargs['filename']:
            antivirus.scan(filename)
        results = map(lambda d: "{0}: {1}".format(d[0], d[1]), antivirus.scan_results.items())
        print("\n".join(results))

    ##########################################################################
    # command line program
    ##########################################################################

    # define command line arguments
    parser = argparse.ArgumentParser(description='Antivirus CLI mode')
    parser.add_argument('antivirus', type=str, choices=antivirus_mapping.keys(), help='filename to scan')
    parser.add_argument('-v', '--verbose', action='count', default=0)
    subparsers = parser.add_subparsers(help='sub-command help')

    # create the info parser
    info_parser = subparsers.add_parser('info', help='show antivirus information')
    info_parser.set_defaults(func=antivirus_info)

    # create the scan parser
    scan_parser = subparsers.add_parser('scan', help='scan given filename list')
    scan_parser.add_argument('filename', type=str, nargs='+', help='filename to scan')
    scan_parser.set_defaults(func=antivirus_scan)

    args = parser.parse_args()

    # set verbosity
    if args.verbose == 1:
        logging.basicConfig(level=logging.INFO)
    elif args.verbose == 2:
        logging.basicConfig(level=logging.DEBUG)

    args = vars(parser.parse_args())
    func = args.pop('func')
    # with 'func' removed, args is now a kwargs with only the specific arguments
    # for each subfunction useful for interactive mode.
    func(**args)
