#!/usr/bin/env python

#
# Copyright (c) 2013-2015 QuarksLab.
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

import argparse
from apiclient import IrmaApiClient, IrmaScanApi, IrmaProbesApi, IrmaError

ADDRESS = "http://www.frontend.irma/api/v1/"

# ================================================
#  Functions print values or raise (Called by UI)
# ================================================


def probe_list(verbose=False):
    cli = IrmaApiClient(ADDRESS, verbose)
    probesapi = IrmaProbesApi(cli)
    res = probesapi.list()
    probelist = res['data']
    print "Available analysis : " + ", ".join(probelist)
    return


def scan_cancel(scanid=None, verbose=False):
    cli = IrmaApiClient(ADDRESS, verbose)
    scanapi = IrmaScanApi(cli)
    scan = scanapi.cancel(scanid)
    cancelled = scan.probes_total - scan.probes_finished
    print "Cancelled {0}/{1} jobs".format(cancelled, scan.probes_total)
    return


def scan_progress(scanid=None, partial=False, verbose=False):
    cli = IrmaApiClient(ADDRESS, verbose)
    scanapi = IrmaScanApi(cli)
    scan = scanapi.get(scanid)
    rate_total = 0
    if scan.is_launched():
        if scan.probes_total != 0:
            rate_total = scan.probes_finished * 100 / scan.probes_total
        if scan.probes_finished != 0:
            print("{0}/{1} jobs finished ".format(scan.probes_finished,
                                                  scan.probes_total) +
                  "({0}%)".format(rate_total))
    else:
        print "Scan status : {0}".format(scan.pstatus)
    if scan.is_finished() or partial:
        scan_results(scanid=scanid, verbose=verbose)
    return


def print_probe_result(probe_result, justify=12):
    name = probe_result.name
    print "\t%s" % (name.ljust(justify)),
    if probe_result.status <= 0:
        probe_res = probe_result.error
    else:
        probe_res = probe_result.results
    try:
        if type(probe_res) == list:
            print ("\n\t " + " " * justify).join(probe_res)
        elif probe_res is None:
            print ('clean')
        elif type(probe_res) == dict:
            print "[...]"
        else:
            print (probe_res.strip())
        return
    except:
        print probe_res


def scan_results(scanid, verbose=False):
    cli = IrmaApiClient(ADDRESS, verbose)
    scanapi = IrmaScanApi(cli)
    scan = scanapi.get(scanid)
    for result in scan.results:
        file_result = scanapi.file_results(scanid, result.result_id)
        print "[{0} (sha256: {1})]".format(file_result.name,
                                           file_result.file_infos.sha256)
        for pr in file_result.probe_results:
            print_probe_result(pr)
    return


def scan(filename=None, force=None, probe=None, verbose=False):
    cli = IrmaApiClient(ADDRESS, verbose)
    scanapi = IrmaScanApi(cli)
    scan = scanapi.new()
    scanapi.add(scan.id, filename)
    scanapi.launch(scan.id, force, probe)
    print "scanid {0} launched".format(scan.id)
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
    except IrmaError, e:
        print "IrmaError: {0}".format(e)
    except Exception, e:
        import traceback
        print traceback.format_exc()
        raise IrmaError("Uncaught exception: {0}".format(e))
