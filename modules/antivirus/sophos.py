import logging, argparse, re

from lib.common.hash import sha256sum
from modules.antivirus.base import Antivirus

log = logging.getLogger(__name__)

class Sophos(Antivirus):

    ##########################################################################
    # constructor and destructor stuff
    ##########################################################################

    def __init__(self, *args, **kwargs):
        # class super class constructor
        super(Sophos, self).__init__(*args, **kwargs)
        # set default antivirus information
        self._name = "Sophos Anti-Virus for Linux"
        # scan tool variables
        self._scan_args = (
            "-archive " # scan inside archives
            "-ss " # only print errors or found viruses
        )
        self._scan_patterns = [
            re.compile(r">>> Virus '(<?P<file>.*)' found in file (?P<name>.*)", re.IGNORECASE)
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
            '/opt/sophos-av/lib/sav', # default location in debian
        ]
        database_patterns = [
            '*.dat', #
            'vdl??.vdb', # 
            'sus??.vdb', # 
            '*.ide', # 
        ]
        results = []
        for pattern in database_patterns:
            result = self.locate(pattern, search_paths)
            results.extend(result)
        return results if results else None

    def get_scan_path(self):
        """return the full path of the scan tool"""
        paths = self.locate("*/savscan", "/opt/sophos-av")
        return paths[0] if paths else None


##############################################################################
# CLI for debug purposes
##############################################################################

def antivirus_info(**kwargs):
    # create antivirus instance
    antivirus = Sophos()
    # build output string
    result  = "name    : {0}\n".format(antivirus.name)
    result += "version : {0}\n".format(antivirus.version)
    result += "database: \n"
    for file in antivirus.database:
        result += "    {0} (sha256 = {1})\n".format(file, sha256sum(file))
    print(result)

def antivirus_scan(**kwargs):
    antivirus = Sophos()
    for filename in kwargs['filename']:
        antivirus.scan(filename)
    results = map(lambda d: "{0}: {1}".format(d[0], d[1]), antivirus.scan_results.items())
    print("\n".join(results))

if __name__ == '__main__':

    # define command line arguments
    parser = argparse.ArgumentParser(description='Sophos Anti-Virus for Unix plugin CLI mode')
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
