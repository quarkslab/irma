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

import sys
import os
pardir = os.path.abspath(os.path.join(__file__, os.path.pardir))
sys.path.append(os.path.dirname(pardir))

import logging
import unittest
# Test config
cwd = os.path.abspath(os.path.dirname(__file__))
os.environ['IRMA_FRONTEND_CFG_PATH'] = cwd
from frontend.helpers.sessions import session_query, session_transaction


from lib.irma.common.utils import IrmaReturnCode, IrmaScanStatus, IrmaProbeType
from lib.common.utils import UUID
from lib.common.compat import timestamp


import frontend.controllers.scanctrl as scanctrl
import frontend.controllers.ftpctrl as ftpctrl
import frontend.controllers.braintasks as braintasks
from lib.irma.common.exceptions import IrmaValueError, IrmaTaskError, \
    IrmaDatabaseError

from frontend.models.sqlobjects import Scan

# Parameter for scan test
PROBES = ['Probe1', 'Probe2']
NB_FILES = 5
FILES = {'file1.bin': 'This is File1 binary data',
         'file2.exe': 'This is File2 binary data',
         'file3.dat': 'This is File3 binary data',
         'file4.scr': 'This is File4 binary data',
         'file5.sys': 'This is File5 binary data'
         }
IP = "192.168.13.37"

# ==================
#  Mock Celery tasks
# ==================


def mock_probe_list(successful=True):
    if successful:
        return PROBES
    else:
        raise IrmaTaskError("Celery timeout - probe_list")


def mock_scan_cancel(scanid, successful=True):
    if successful:
        return {"total": NB_FILES,
                "finished": NB_FILES - 2,
                "cancelled": 2}
    else:
        return (IrmaReturnCode.warning, IrmaScanStatus.empty)


def mock_scan_progress(scanid, successful=True):
    if successful:
        return {"total": NB_FILES, "finished": 2, "successful": 2}
    else:
        raise IrmaValueError(IrmaScanStatus.empty)


def void(*_):
    pass

braintasks.probe_list = mock_probe_list
braintasks.cancel = mock_scan_cancel
braintasks.progress = mock_scan_progress
braintasks.scan_launch = void
ftpctrl.upload_scan = void


# =================
#  Logging options
# =================

def enable_logging(level=logging.INFO,
                   handler=None,
                   formatter=None):
    global log
    log = logging.getLogger()
    if formatter is None:
        formatter = logging.Formatter("%(asctime)s [%(name)s] " +
                                      "%(levelname)s: %(message)s")
    if handler is None:
        handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.setLevel(level)


# ============
#  Test cases
# ============

class scanctrlTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def assertListContains(self, list1, list2):
        for l in list1:
            self.assertIn(l, list2)


def get_fake_results(probe):
    fake_res = {}
    fake_res['name'] = probe
    fake_res['version'] = 'FAKE-{0}'.format(timestamp())
    fake_res['duration'] = 0.2
    fake_res['type'] = IrmaProbeType.antivirus
    fake_res['status'] = 1
    return fake_res


def fake_scan_launch(scanid):
    probes = scanctrl.launch_synchronous(scanid, True, None)
    scanctrl.launch_asynchronous(scanid, True)
    with session_transaction() as session:
        scan = Scan.load_from_ext_id(scanid, session)
        scan.set_status(IrmaScanStatus.launched, session)
    return probes


class TestScanController(scanctrlTestCase):
    # ==========
    #  SCAN NEW
    # ==========
    def test_scan_new_id(self):
        # test we got an id
        scanid = scanctrl.new(IP)
        self.assertIsNotNone(scanid)

    def test_scan_new_status(self):
        # test we have a correct status
        scanid = scanctrl.new(IP)
        with session_query() as session:
            scan = Scan.load_from_ext_id(scanid, session)
            self.assertIsNotNone(scan.date)
            self.assertEqual(scan.status, IrmaScanStatus.empty)
            self.assertEqual(scan.ip, IP)
            self.assertFalse(scanctrl.finished(scanid))

    # ==========
    #  SCAN ADD
    # ==========
    def test_scan_add_unknown_id(self):
        with self.assertRaises(IrmaDatabaseError):
            scanctrl.add_files(UUID.generate(), FILES)

    def test_scan_add_wrong_status(self):
        scanid = scanctrl.new(IP)
        for status in IrmaScanStatus.label.keys():
            if status <= IrmaScanStatus.ready:
                continue
            with session_transaction() as session:
                scan = Scan.load_from_ext_id(scanid, session)
                scan.set_status(status, session)
            with self.assertRaises(IrmaValueError):
                scanctrl.add_files(scanid, FILES)

    def test_scan_add(self):
        scanid = scanctrl.new(IP)
        res = scanctrl.add_files(scanid, FILES)
        self.assertEqual(res, NB_FILES)

        with session_query() as session:
            scan = Scan.load_from_ext_id(scanid, session)
            self.assertIsNotNone(scan.date)
            self.assertEqual(scan.status, IrmaScanStatus.ready)
            self.assertEqual(len(scan.files_web), NB_FILES)
            self.assertEqual(len((scan.files_web[0]).probe_results), 0)
            self.assertFalse(scanctrl.finished(scanid))

    # =============
    #  SCAN LAUNCH
    # =============

    def test_scan_launch_unknown_id(self):
        with self.assertRaises(IrmaDatabaseError):
            scanctrl.add_files(UUID.generate(), FILES)

    def test_scan_launch_wrong_status(self):
        scanid = scanctrl.new(IP)
        for status in IrmaScanStatus.label.keys():
            if status == IrmaScanStatus.ready:
                continue
            with session_transaction() as session:
                scan = Scan.load_from_ext_id(scanid, session)
                scan.set_status(status, session)
            with self.assertRaises(IrmaValueError):
                fake_scan_launch(scanid)

    def test_scan_launch(self):
        scanid = scanctrl.new(IP)
        self.assertEqual(scanctrl.add_files(scanid, FILES), len(FILES))
        self.assertEqual(fake_scan_launch(scanid), PROBES)

        with session_query() as session:
            scan = Scan.load_from_ext_id(scanid, session)
            self.assertIsNotNone(scan.date)
            self.assertEqual(scan.status, IrmaScanStatus.launched)
            self.assertEqual(len(scan.files_web), NB_FILES)
            self.assertEqual(len((scan.files_web[0]).probe_results),
                             len(PROBES))
            self.assertFalse(scanctrl.finished(scanid))
            for fw in scan.files_web:
                probelist = [pr.probe_name for pr in fw.probe_results]
                self.assertListContains(PROBES, probelist)
            self.assertFalse(scanctrl.finished(scanid))

    def test_scan_partial_results(self):
        scanid = scanctrl.new(IP)
        self.assertEqual(scanctrl.add_files(scanid, FILES),
                         len(FILES))
        self.assertEqual(fake_scan_launch(scanid), PROBES)

        with session_transaction() as session:
            scan = Scan.load_from_ext_id(scanid, session)
            self.assertEqual(scan.status, IrmaScanStatus.launched)
            sha256 = scan.files_web[0].file.sha256
            # add fake results to scan
            scanctrl.set_result(scanid,
                                sha256,
                                PROBES[0],
                                get_fake_results(PROBES[0]))
            self.assertFalse(scanctrl.finished(scanid))
            results = scanctrl.result(scanid)
            self.assertEqual(type(results), dict)
            self.assertEqual(len(results.keys()), NB_FILES)

    def test_scan_full_results(self):
        scanid = scanctrl.new(IP)
        self.assertEqual(scanctrl.add_files(scanid, FILES), len(FILES))
        self.assertEqual(fake_scan_launch(scanid), PROBES)
        files_sha256 = []
        with session_query() as session:
            scan = Scan.load_from_ext_id(scanid, session)
            self.assertEqual(scan.status, IrmaScanStatus.launched)
            # add all fake results to scan
            for fw in scan.files_web:
                files_sha256.append(fw.file.sha256)

        # add fake results to all files/ all probes
        for p in PROBES:
            for sha256 in files_sha256:
                scanctrl.set_result(scanid,
                                    sha256,
                                    p,
                                    get_fake_results(p))

        results = scanctrl.result(scanid)
        self.assertEqual(type(results), dict)
        self.assertEqual(len(results.keys()), NB_FILES)
        for (_, res_dict) in results.items():
            self.assertEqual(len(res_dict['results']), len(PROBES))
        self.assertTrue(scanctrl.finished(scanid))

if __name__ == '__main__':
    enable_logging()
    unittest.main()
