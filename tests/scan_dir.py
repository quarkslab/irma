#
# Copyright (c) 2014 QuarksLab.
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
import json
import datetime
import random
import hashlib
import signal
import sys
from frontend.cli.irma import _scan_new, _scan_add, _scan_launch, \
    _scan_progress, _scan_cancel, IrmaScanStatus, _scan_result
import time

RES_PATH = "."
SRC_PATH = "."

DEBUG = True
SCAN_TIMEOUT_SEC = 300
BEFORE_NEXT_PROGRESS = 5
DEBUG = False
Probelist = [u'ClamAV', u'VirusTotal', u'Kaspersky', u'Sophos',
             u'McAfeeVSCL', u'Symantec', u'StaticAnalyzer']

scanner = None


def handler(*_):
    print 'Cancelling...'
    if scanner is not None:
        scanner.cancel()
    sys.exit(0)


class ScannerError(Exception):
    pass


class Scanner(object):
    def __init__(self):
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
            _scan_cancel(self.scanid, DEBUG)

    def scan_files(self, files,
                   force=False,
                   probe=None,
                   timeout=SCAN_TIMEOUT_SEC):
        self.scanid = _scan_new(DEBUG)
        _scan_add(self.scanid, files, DEBUG)
        probelist = _scan_launch(self.scanid, force, probe, DEBUG)
        scanid = self.scanid
        nb = len(files)
        probes = " - ".join(sorted(probelist))
        print("launching scan {0}".format(scanid) +
              " of {0} files on {1}".format(scanid, nb, probes))
        start = time.time()
        while True:
            time.sleep(BEFORE_NEXT_PROGRESS)
            (status, fin, tot, suc) = _scan_progress(self.scanid, DEBUG)
            if fin is not None:
                # write in place
                sys.stdout.write("\r\tjobs {0}({1})/{2}".format(fin, suc, tot))
                sys.stdout.flush()
            if status == IrmaScanStatus.label[IrmaScanStatus.finished]:
                break
            now = time.time()
            if now > (start + timeout):
                _scan_cancel(self.scanid, DEBUG)
                raise ScannerError("Results Timeout")
        return _scan_result(self.scanid, DEBUG)

    def _write_result(self, res):
        print "Writing results"
        for (sha256, results) in res.items():
            res_file = os.path.join(self.res_dir, sha256)
            with open(res_file, "w") as dst:
                dst.write(json.dumps(results))
        return

    def _write_timeout_result(self, file_list):
        print "Timeout results"
        for tf in file_list:
            with open(tf) as t:
                sha256 = hashlib.sha256(t.read()).hexdigest()
            res_file = os.path.join(self.res_dir, sha256)
            with open(res_file, "w") as dst:
                dst.write("timeout")

    def scan_dir(self, dirname, nb_files_per_scan):
        if not os.path.exists(dirname):
            raise ScannerError("dir to scan does not exits")

        # get all files in dir
        filenames = []
        for _, _, filename in os.walk(dirname):
            for f in filename:
                filenames.append(os.path.join(dirname, f))
        random.shuffle(filenames)
        for i in xrange(0, len(filenames), nb_files_per_scan):
            file_list = filenames[i:i + nb_files_per_scan]
            try:
                res = self.scan_files(file_list, force=True)
            except ScannerError:
                self._write_timeout_result(file_list)
                res = _scan_result(self.scanid, DEBUG)
            self._write_result(res)
        return

signal.signal(signal.SIGTERM, handler)
signal.signal(signal.SIGINT, handler)
scanner = Scanner()
scanner.scan_dir("samples", 5)
