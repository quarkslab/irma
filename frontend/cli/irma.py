#!/usr/bin/env python

import requests
import json
import argparse

ADDRESS = "http://frontend.irma.qb/_api"


class IrmaReturnCode:
    success = 0
    warning = 1
    error = -1
    label = {success: "success", warning: "warning", error: "error"}


class IrmaError(Exception):
    """Error on cli script"""
    pass


# Warning this is a copy of IrmaScanStatus lib.irma.common.utils
# in order to get rid of this dependency
# KEEP SYNCHRONIZED
class IrmaScanStatus:
    created = 0
    launched = 10
    cancelling = 20
    cancelled = 21
    processed = 30
    finished = 50
    flushed = 100
    label = {
        created: "created",
        launched: "launched",
        cancelling: "being cancelled",
        cancelled: "cancelled",
        processed: "processed",
        finished: "finished",
        flushed: "flushed"
    }


# =============================================================
#  Functions returns values or raise (Called by other program)
# =============================================================

def _generic_get_call(url, kwname, verbose):
    resp = requests.get(url)
    data = json.loads(resp.content)
    if verbose:
        print data
    if data['code'] == IrmaReturnCode.success:
        return data[kwname]
    else:
        code = IrmaReturnCode.label[data['code']]
        reason = "{0}: {1}".format(code, data['msg'])
        raise IrmaError(reason)
    return


def _ping(verbose=False):
    return _generic_get_call(ADDRESS, 'msg', verbose)


def _probe_list(verbose=False):
    url = ADDRESS + '/probe/list'
    return _generic_get_call(url, 'probe_list', verbose)


def _scan_cancel(scanid, verbose=False):
    url = ADDRESS + '/scan/cancel/' + scanid
    return _generic_get_call(url, 'cancel_details', verbose)


def _scan_result(scanid, verbose=False):
    url = ADDRESS + '/scan/result/' + scanid
    return _generic_get_call(url, 'scan_results', verbose)


def _scan_new(verbose=False):
    url = ADDRESS + '/scan/new'
    return _generic_get_call(url, 'scan_id', verbose)


def _scan_progress(scanid, verbose=False):
    resp = requests.get(url=ADDRESS + '/scan/progress/' + scanid)
    data = json.loads(resp.content)
    if verbose:
        print data
    status = None
    finished = None
    successful = None
    total = None
    if data['code'] == IrmaReturnCode.success:
        status = IrmaScanStatus.label[IrmaScanStatus.launched]
        results = data['progress_details']
        finished = results['finished']
        successful = results['successful']
        total = results['total']
    elif data['code'] == IrmaReturnCode.warning:
        status = data['msg']
    else:
        code = IrmaReturnCode.label[data['code']]
        reason = "{0} getting progress: {1}".format(code, data['msg'])
        raise IrmaError(reason)
    return (status, finished, total, successful)


def _scan_add(scanid, filelist, verbose=False):
    postfiles = dict(map(lambda t: (t, open(t, 'rb')), filelist))
    resp = requests.post(ADDRESS + '/scan/add/' + scanid, files=postfiles)
    data = json.loads(resp.content)
    if verbose:
        print data
    if data['code'] != IrmaReturnCode.success:
        raise IrmaError("{0}: {1}".format(data['code'], data['msg']))
    return data['nb_files']


def _scan_launch(scanid, force, probe, verbose=False):
    params = {'force': force}
    if probe:
        params['probe'] = ','.join(probe)
    resp = requests.get(ADDRESS + '/scan/launch/' + scanid, params=params)
    data = json.loads(resp.content)
    if verbose:
        print data
    if data['code'] != IrmaReturnCode.success:
        code = IrmaReturnCode.label[data['code']]
        reason = "{0} launching scan: {1}".format(code, data['msg'])
        raise IrmaError(reason)
    else:
        probelist = data['probe_list']
    return probelist


# ================================================
#  Functions print values or raise (Called by UI)
# ================================================


def probe_list(verbose=False):
    probelist = _probe_list(verbose)
    print "Available analysis : " + ", ".join(probelist)
    return


def scan_cancel(scanid=None, verbose=False):
    print _scan_cancel(scanid, verbose)
    return


def scan_progress(scanid=None, partial=None, verbose=False):
    (status, finished, total, successful) = _scan_progress(scanid, verbose)
    if status == IrmaScanStatus.label[IrmaScanStatus.launched]:
        rate_total = rate_success = 0
        if total != 0:
            rate_total = finished * 100 / total
        if finished != 0:
            rate_success = successful * 100 / finished
            print("{0}/{1} jobs finished ".format(finished, total) +
                  "({0}%) / ".format(rate_total) +
                  "{0} success ({1}%)".format(successful, rate_success))
    else:
        print "Scan status : {0}".format(status)
    if status == IrmaScanStatus.label[IrmaScanStatus.finished] or partial:
        scan_results(scanid=scanid, verbose=verbose)
    return


def print_results(list_res, justify=12):
    for (hashval, info) in list_res.items():
        name = info['filename']
        res = info['results']
        print "{0}\n[SHA256: {1}]".format(name, hashval)
        for av in res:
            print "\t%s" % (av.ljust(justify)),
            avres = res[av].get('result', "No result")
            if type(avres) == str:
                print(avres.strip())
            elif type(avres) == list:
                print("\n\t " + " " * justify).join(avres)
            elif avres is None:
                print('clean')
            else:
                print avres


def scan_results(scanid=None, verbose=False):
    print_results(_scan_result(scanid, verbose))
    return


def scan(filename=None, force=None, probe=None, verbose=False):
    scanid = _scan_new(verbose)
    _scan_add(scanid, filename, verbose)
    _scan_launch(scanid, force, probe, verbose)
    print "scanid {0} launched".format(scanid)
    return

if __name__ == "__main__":
    # create the top-level parser
    desc = "command line interface for IRMA"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-v',
                        dest='verbose',
                        action='store_true',
                        help='verbose output')
    subparsers = parser.add_subparsers(help='sub-command help')

    # create the parser for the "list" command
    list_parser = subparsers.add_parser('list', help='list available analysis')
    list_parser.set_defaults(func=probe_list)

    # create the parser for the "scan" command
    scan_parser = subparsers.add_parser('scan',
                                        help='scan given filename list')
    scan_parser.add_argument('--force',
                             dest='force',
                             action='store_true',
                             help='force new analysis')
    scan_parser.add_argument('--probe',
                             nargs='+',
                             help='specify analysis list')
    scan_parser.add_argument('--filename',
                             nargs='+',
                             help='a filename to analyze',
                             required=True)
    scan_parser.set_defaults(func=scan)

    # create the parser for the "results" command
    res_parser = subparsers.add_parser('results',
                                       help='print scan results')
    res_parser.add_argument('--partial',
                            dest='partial',
                            action='store_true',
                            help='print results as soon as they are available')
    res_parser.add_argument('scanid', help='scanid returned by scan command')
    res_parser.set_defaults(func=scan_progress)

    # create the parser for the "cancel" command
    cancel_parser = subparsers.add_parser('cancel', help='cancel scan')
    cancel_parser.add_argument('scanid',
                               help='scanid returned by scan command')
    cancel_parser.set_defaults(func=scan_cancel)

    args = vars(parser.parse_args())
    func = args.pop('func')
    # with 'func' removed, args is now a kwargs with only
    # the specific arguments for each subfunction
    # useful for interactive mode.
    try:
        func(**args)
    except requests.exceptions.ConnectionError:
        print "Error connecting to frontend"
    except IrmaError, e:
        print "IrmaError: {0}".format(e)
    except Exception, e:
        raise IrmaError("Uncaught exception: {0}".format(e))
