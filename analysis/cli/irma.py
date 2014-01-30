import requests
import json
import sys
import argparse

# ADDRESS = "http://brain.irma.qb:8080"
ADDRESS = "http://192.168.130.133:8080"


def probe_list():
    try:
        resp = requests.get(url=ADDRESS + '/probe_list')
        data = json.loads(resp.content)
        if data['result'] == "success":
            print "Available analysis : " + ", ".join(data["info"])
    except requests.exceptions.ConnectionError:
        print "Error connecting to frontend"
    except Exception, e:
        print "Error getting analysis list: %s", e
    return

def scan_cancel(scanid=None):
    try:
        resp = requests.get(url=ADDRESS + '/scan/cancel/' + scanid)
        print resp.content
    except requests.exceptions.ConnectionError:
        print "Error connecting to frontend"
    return


def scan_status(scanid=None):
    try:
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
                scan_results(scanid=scanid)
        elif data['result'] == 'warning' and data['info'] == "finished":
            scan_results(scanid=scanid)
        else:
            print data['info']
    except requests.exceptions.ConnectionError:
        print "Error connecting to frontend"
    except Exception, e:
        print "Error getting scan status: %s" % e
    return

def print_results(list_res, justify=12):
    for (name, res) in list_res.items():
        print "%s" % name
        for av in res:
            print "\t%s" % (av.ljust(justify)),
            avres = res[av]['result']
            if type(avres) == str:
                print avres.strip()
            elif type(avres) == list:
                print ("\n\t " + " "*justify).join(avres)
            else:
                print avres

def scan_results(scanid=None):
    try:
        resp = requests.get(url=ADDRESS + '/scan/results/' + scanid)
        data = json.loads(resp.content)
        if data['result'] == "success":
            list_res = data['info']
        else:
            sys.exit(0)
        print_results(list_res)
    except requests.exceptions.ConnectionError:
        print "Error connecting to frontend"
    except Exception, e:
        print "Error getting scan results: %s" % e
    return

def scan(filename=None, force=None, probe=None):
    try:
        postfiles = dict(map(lambda t: (t, open(t, 'rb')), filename))
        params = {'force':force}
        if probe:
            params['probe'] = ','.join(probe)
        resp = requests.post(ADDRESS + '/scan', files=postfiles, params=params)
        data = json.loads(resp.content)
        if data['result'] == "success":
            scanid = data['info']['scanid']
            print "scanid:", scanid
    except requests.exceptions.ConnectionError:
        print "Error connecting to frontend"
    except Exception, e:
        print "Error creating new scan: %s" % e
    return

if __name__ == "__main__":
    # create the top-level parser
    parser = argparse.ArgumentParser(description='command line interface for IRMA')
    subparsers = parser.add_subparsers(help='sub-command help')

    # create the parser for the "list" command
    list_parser = subparsers.add_parser('list', help='list available analysis')
    list_parser.set_defaults(func=probe_list)

    # create the parser for the "scan" command
    scan_parser = subparsers.add_parser('scan', help='scan given filename list')
    scan_parser.add_argument('--force', dest='force', action='store_true', help='force new analysis')
    scan_parser.add_argument('--probe', nargs='+', help='specify analysis list')
    scan_parser.add_argument('--filename', nargs='+', help='a filename to analyze', required=True)
    scan_parser.set_defaults(func=scan)

    # create the parser for the "results" command
    res_parser = subparsers.add_parser('results', help='print scan results')
    res_parser.add_argument('scanid', help='scanid returned by scan command')
    res_parser.set_defaults(func=scan_status)

    # create the parser for the "cancel" command
    cancel_parser = subparsers.add_parser('cancel', help='cancel scan')
    cancel_parser.add_argument('scanid', help='scanid returned by scan command')
    cancel_parser.set_defaults(func=scan_cancel)

    args = vars(parser.parse_args())
    func = args.pop('func')
    # with 'func' removed, args is now a kwargs with only
    # the specific arguments for each subfunction
    # useful for interactive mode.
    func(**args)
