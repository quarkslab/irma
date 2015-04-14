#!/usr/bin/env python

#
# Copyright (c) 2013-2014 QuarksLab.
# This file is part of IRMA project.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License in the top-level directory
# of this distribution and at:
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# No part of the project, including this file, may be copied,
# modified, propagated, or distributed except according to the
# terms contained in the LICENSE file.

import requests
import json
import argparse

ADDRESS = "http://172.16.1.30/api/v1/"


# Warning this is a copy of IrmaScanStatus lib.irma.common.utils
# in order to get rid of this dependency
# KEEP SYNCHRONIZED

class IrmaScanStatus:
    empty = 0
    ready = 10
    uploaded = 20
    launched = 30
    processed = 40
    finished = 50
    flushed = 60
    # cancel
    cancelling = 100
    cancelled = 110
    # errors
    error = 1000
    # Probes 101x
    error_probe_missing = 1010
    error_probe_na = 1011
    # FTP 102x
    error_ftp_upload = 1020

    label = {empty: "empty",
             ready: "ready",
             uploaded: "uploaded",
             launched: "launched",
             processed: "processed",
             finished: "finished",
             cancelling: "cancelling",
             cancelled: "cancelled",
             flushed: "flushed",
             error: "error",
             error_probe_missing: "probelist missing",
             error_probe_na: "probe(s) not available",
             error_ftp_upload: "ftp upload error"
             }


class IrmaError(Exception):
    """Error on cli script"""
    pass


# =============================================================
#  Functions returns values or raise (Called by other program)
# =============================================================

def _generic_get_call(url, verbose):
    resp = requests.get(url)
    if verbose:
        print "http code : {0}".format(resp.status_code)
        print "content : {0}".format(resp.content)
    if resp.status_code == 200:
        return json.loads(resp.content)
    else:
        reason = "Erreur Http code {0}".format(resp.status_code)
        try:
            data = json.loads(resp.content)
            if 'message' in data:
                reason += data['message']
        except:
            pass
        raise IrmaError(reason)


def _generic_post_call(url, verbose, **extra_args):
    resp = requests.post(url, **extra_args)
    if verbose:
        print "http code : {0}".format(resp.status_code)
        print "content : {0}".format(resp.content)
    if resp.status_code == 200:
        return json.loads(resp.content)
    else:
        reason = "Erreur Http code {0}".format(resp.status_code)
        try:
            data = json.loads(resp.content)
            if 'message' in data:
                reason += ": {0}".format(data['message'])
        except:
            pass
        raise IrmaError(reason)


def _ping(verbose=False):
    return _generic_get_call(ADDRESS, 'msg', verbose)


def _probe_list(verbose=False):
    url = ADDRESS + '/probes'
    data = _generic_get_call(url, verbose)
    return data['data']


def _scan_cancel(scanid, verbose=False):
    url = ADDRESS + '/scans/{0}/cancel'.format(scanid)
    data = _generic_post_call(url, verbose)
    return (data['probes_finished'], data['probes_total'])


def _scan_result(scanid, verbose=False):
    url = ADDRESS + '/scans/{0}/results'.format(scanid)
    data = _generic_get_call(url, verbose)
    return data


def _scan_file_result(scanid, scan_file_idx, verbose=False):
    url = ADDRESS + '/scans/{0}/results/{1}'.format(scanid, scan_file_idx)
    data = _generic_get_call(url, verbose)
    return data


def _scan_new(verbose=False):
    url = ADDRESS + '/scans'
    data = _generic_post_call(url, verbose)
    return data['id']


def _scan_add(scanid, filelist, verbose=False):
    postfiles = dict(map(lambda t: (t, open(t, 'rb')), filelist))
    url = ADDRESS + '/scans/{0}/files'.format(scanid)
    data = _generic_post_call(url, verbose, files=postfiles)
    return len(data['results'])


def _scan_launch(scanid, force, probe, verbose=False):
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    params = {'force': force}
    if probe is not None:
        params['probes'] = ','.join(probe)
    url = ADDRESS + "/scans/{0}/launch".format(scanid)
    data = _generic_post_call(url, verbose,
                              data=json.dumps(params), headers=headers)
    return data


def _scan_progress(scanid, verbose=False):
    url = ADDRESS + '/scans/{0}'.format(scanid)
    data = _generic_get_call(url, verbose)
    return (data['status'], data['probes_finished'],
            data['probes_total'])

# ================================================
#  Functions print values or raise (Called by UI)
# ================================================


def probe_list(verbose=False):
    probelist = _probe_list(verbose)
    print "Available analysis : " + ", ".join(probelist)
    return


def scan_cancel(scanid=None, verbose=False):
    (finished, total) = _scan_cancel(scanid, verbose)
    print "Cancelled {0}/{1} jobs".format(total - finished, total)
    return


def scan_progress(scanid=None, partial=None, verbose=False):
    (status, finished, total) = _scan_progress(scanid, verbose)
    rate_total = 0
    if status == IrmaScanStatus.launched:
        if total != 0:
            rate_total = finished * 100 / total
        if finished != 0:
            print("{0}/{1} jobs finished ".format(finished, total) +
                  "({0}%)".format(rate_total))
    else:
        print "Scan status : {0}".format(IrmaScanStatus.label[status])
    if status == IrmaScanStatus.finished or partial:
        scan_results(scanid=scanid, verbose=verbose)
    return


def print_results(results_dict, justify=12):
    for (hashval, fileres) in results_dict.items():
        if 'probe_results' not in fileres:
            print "Wrong return format"
            print results_dict
            return
        probe_results = fileres['probe_results']
        filename = fileres['name']
        print "{0}\n[SHA256: {1}]".format(filename, hashval)
        for probe in probe_results:
            name = probe['name']
            print "\t%s" % (name.ljust(justify)),
            probe_res = probe.get('results', "No result")
            if type(probe_res) == str:
                print(probe_res.strip())
            elif type(probe_res) == list:
                print("\n\t " + " " * justify).join(probe_res)
            elif probe_res is None:
                print('clean')
            elif type(probe_res) == dict:
                print "[...]"
            else:
                print(probe_res)


def scan_results(scanid=None, verbose=False):
    scan_results = _scan_result(scanid, verbose)
    res = {}
    for scan_file in scan_results:
        file_idx = scan_file['result_id']
        data = _scan_file_result(scanid, file_idx, verbose)
        hashval = data['file_infos']['sha256']
        res[hashval] = data
    print_results(res)
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
