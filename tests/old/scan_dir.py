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

import os
import datetime
import random
import hashlib
import signal
import sys
import time
# irma-frontend should be in path
from frontend.cli.apiclient import IrmaApiClient, IrmaScanApi, IrmaProbesApi, \
    IrmaError

RES_PATH = "."
SRC_PATH = "."

API_ADDRESS = 'http://www.frontend.irma/api/v1'
DEBUG = False
BEFORE_NEXT_PROGRESS = 2
ProbeWlist = None
ProbeBlist = None
scanner = None


def handler(*_):
    print 'Cancelling...'
    if scanner is not None:
        try:
            scanner.cancel()
        except IrmaError as e:
            print(str(e))
    sys.exit(0)

signal.signal(signal.SIGTERM, handler)
signal.signal(signal.SIGINT, handler)


class ScannerError(Exception):
    pass


class Scanner(object):
    def __init__(self, api_url, verbose=False):
        api_client = IrmaApiClient(api_url, verbose)
        self.scanapi_client = IrmaScanApi(api_client)
        self.probesapi_client = IrmaProbesApi(api_client)
        self.probe_list = None
        self._probe_list()
        # test setup
        date_str = str(datetime.datetime.now().date())
        date_str = date_str.replace('-', '')
        self.res_dir = os.path.join(RES_PATH, date_str)
        self.scanid = None
        try:
            if not os.path.exists(self.res_dir):
                os.mkdir(self.res_dir)
        except OSError:
            raise ScannerError("Can't create [{0}]".format(self.res_dir))

    def cancel(self):
        if self.scanid is not None:
            self.scanapi_client.cancel(self.scanid)

    def _probe_list(self):
        probe_list = self.probesapi_client.list().get('data', [])
        if ProbeWlist is not None:
            probe_list = filter(lambda x: x in ProbeWlist, probe_list)
        if ProbeBlist is not None:
            probe_list = filter(lambda x: x not in ProbeBlist, probe_list)
        self.probe_list = probe_list

    def fetch_scan(self):
        if self.scanid is None:
            raise ScannerError("Empty scanid")
        return self.scanapi_client.get(self.scanid)

    def get_results(self):
        scan = self.fetch_scan()
        res = []
        for result in scan.results:
            file_result = self.scanapi_client.file_results(self.scanid,
                                                           result.result_id)
            res.append(file_result)
        return res

    def scan_files(self, files,
                   force=False,
                   timeout_per_file=30):
        scan = self.scanapi_client.new()
        self.scanid = scan.id
        self.scanapi_client.add(self.scanid, files)
        self.scanapi_client.launch(self.scanid, force, self.probe_list)
        nb = len(files)
        timeout = timeout_per_file * nb
        print("launching scan {0}".format(self.scanid) +
              " of {0} files on {1} probes".format(nb, len(self.probe_list)))
        start = time.time()
        while True:
            time.sleep(BEFORE_NEXT_PROGRESS)
            scan = self.fetch_scan()
            # write in place
            sys.stdout.write("\r\tjobs {0}/{1}".format(scan.probes_finished,
                                                       scan.probes_total))
            sys.stdout.flush()
            if scan.is_finished():
                break
            now = time.time()
            if now > (start + timeout):
                try:
                    self.cancel()
                except:
                    pass
                raise ScannerError("Results Timeout")
        return self.get_results()

    def _write_result(self, res_list):
        print " -> Writing results"
        for res in res_list:
            sha256 = res.file_infos.sha256
            res_file = os.path.join(self.res_dir, sha256)
            with open(res_file, "w") as dst:
                for result in res.probe_results:
                    dst.write(result.to_json() + "\n")
        return

    def _write_timeout_result(self, file_list):
        print " -> Timeout results"
        for tf in file_list:
            with open(tf) as t:
                sha256 = hashlib.sha256(t.read()).hexdigest()
            res_file = os.path.join(self.res_dir, sha256)
            with open(res_file, "w") as dst:
                dst.write("timeout")

    def scan_dir(self, dirname, nb_files_per_scan):
        # get all files in dir
        filenames = []
        for _, _, filename in os.walk(dirname):
            for f in filename:
                filenames.append(os.path.join(dirname, f))
        print 'Found {0} files to scan in {1}'.format(len(filenames), dirname)
        random.shuffle(filenames)
        for i in xrange(0, len(filenames), nb_files_per_scan):
            file_list = filenames[i:i + nb_files_per_scan]
            try:
                res = self.scan_files(file_list,
                                      force=True)
            except ScannerError:
                self._write_timeout_result(file_list)
                res = self.get_results()
            self._write_result(res)
        return


if __name__ == "__main__":
    if len(sys.argv) not in [2, 3]:
        print("IRMA directory scanner")
        print("Usage: {0} <directory name>".format(__file__) +
              "<nb file per scan " +
              "(default:5)>")
        sys.exit(0)
    directory = os.path.abspath(sys.argv[1])
    if not os.path.exists(directory):
        print("[!] directory to scan does not exits")
        sys.exit(-1)
    if len(sys.argv) == 3:
        nb_file_per_scan = int(sys.argv[2])
    else:
        nb_file_per_scan = 5
    scanner = Scanner(API_ADDRESS, DEBUG)
    scanner.scan_dir(directory, nb_file_per_scan)
