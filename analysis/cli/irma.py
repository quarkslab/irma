import requests
import json
import sys
import argparse

# ADDRESS = "http://brain.irma.qb:8080"
# ADDRESS = "http://192.168.130.133:8080"
ADDRESS = "http://localhost:8080"


def sonde_list(args):
    resp = requests.get(url=ADDRESS + '/sonde_list')
    print resp.content
    return

def scan_cancel(args):
    scanid = args.scanid
    resp = requests.get(url=ADDRESS + '/scan/cancel/' + scanid)
    print resp.content
    return


def scan_status(args):
    scanid = args.scanid
    resp = requests.get(url=ADDRESS + '/scan/progress/' + scanid)
    data = json.loads(resp.content)
    if data['result'] == "success":
        results = data['info']
        finished = results['finished']
        successful = results['successful']
        total = results['total']
        rate_total = rate_success = 0
        if total != 0 : rate_total = finished * 100 / total
        if finished != 0 : rate_success = successful * 100 / finished
        print "%d/%d jobs finished (%d%%) / %d successful (%d%%)" % (finished, total, rate_total, successful, rate_success)
        if finished == total:
            scan_results(scanid)
    elif data['result'] == 'warning' and data['info'] == "finished":
        scan_results(scanid)
    else:
        print data['info']
    return

def scan_results(scanid):
    resp = requests.get(url=ADDRESS + '/scan/results/' + scanid)
    data = json.loads(resp.content)
    if data['result'] == "success":
        files = data['info']
    else:
        sys.exit(0)
    for (name, res) in files.items():
        print "%s" % name
        for av in res:
            print "\t%s%s" % (av.ljust(12), res[av]['result'].strip())
    return


def scan(args):
    postfiles = dict(map(lambda t: (t, open(t, 'rb')), args.filenames))
    resp = requests.post(ADDRESS + '/scan', files=postfiles, params={'force':args.force, 'sondelist':args.sonde})
    data = json.loads(resp.content)

    if data['result'] == "success":
        scanid = data['info']['scanid']
        print "Scanid:", scanid
    else:
        raise 'Error'
    return

# create the top-level parser
parser = argparse.ArgumentParser(description='command line interface for IRMA')
subparsers = parser.add_subparsers(help='sub-command help')

# create the parser for the "list" command
list_parser = subparsers.add_parser('list', help='list available analysis')
list_parser.set_defaults(func=sonde_list)

# create the parser for the "scan" command
scan_parser = subparsers.add_parser('scan', help='scan given filename list')
scan_parser.add_argument('filenames', nargs='+', help='a filename to analyze')
scan_parser.add_argument('--force', dest='force', action='store_true', help='force new analysis')
scan_parser.add_argument('--sonde', nargs='+', help='specify analysis list')
scan_parser.set_defaults(func=scan)

# create the parser for the "results" command
res_parser = subparsers.add_parser('results', help='print scan results')
res_parser.add_argument('scanid', help='scanid returned by scan command')
res_parser.set_defaults(func=scan_status)

# create the parser for the "cancel" command
cancel_parser = subparsers.add_parser('cancel', help='cancel scan')
cancel_parser.add_argument('scanid', help='scanid returned by scan command')
cancel_parser.set_defaults(func=scan_cancel)

args = parser.parse_args()
args.func(args)
