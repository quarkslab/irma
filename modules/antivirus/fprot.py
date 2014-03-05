import logging, argparse, re, os

from lib.common.hash import sha256sum
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
            database_path = self.locate('antivir.def', dirname)
            result = database_path
        return result

    def get_scan_path(self):
        """return the full path of the scan tool"""
        paths = self.locate("fpscan", "/usr/local/f-prot/")
        return paths[0] if paths else None


##############################################################################
# CLI for debug purposes
##############################################################################

def antivirus_info(**kwargs):
    # create antivirus instance
    antivirus = FProt()
    # build output string
    result  = "name    : {0}\n".format(antivirus.name)
    result += "version : {0}\n".format(antivirus.version)
    result += "database: \n"
    for file in antivirus.database:
        result += "    {0} (sha256 = {1})\n".format(file, sha256sum(file))
    print(result)

def antivirus_scan(**kwargs):
    antivirus = FProt()
    for filename in kwargs['filename']:
        antivirus.scan(filename)
    results = map(lambda d: "{0}: {1}".format(d[0], d[1]), antivirus.scan_results.items())
    print("\n".join(results))

if __name__ == '__main__':

    # define command line arguments
    parser = argparse.ArgumentParser(description='FProtAV plugin CLI mode')
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
