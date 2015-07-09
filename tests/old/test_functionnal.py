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

import unittest
import os
from frontend.cli.irma import _scan_new, _scan_add, _probe_list, \
    _scan_launch, _scan_progress, _scan_cancel, IrmaScanStatus, \
    _scan_result, IrmaError
import time

SCAN_TIMEOUT_SEC = 30
BEFORE_NEXT_PROGRESS = 5
DEBUG = True
EICAR_NAME = "eicar.com"
EICAR_HASH = '275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f'
EICAR_RESULTS = {
    # u'NSRL': {u'result': [u'eicar.com.txt,68,18115,358,']},
    u'ClamAV': {
        u'version': u'ClamAV 0.97.8/18526/Sat Mar  1 22:54:55 2014',
        u'result': u'Eicar-Test-Signature'},
    u'VirusTotal': {
        u'result': u'detected by 36/38'},
    u'Kaspersky': {
        u'version': u'Kaspersky Anti-Virus (R) 14.0.0.4837',
        u'result': u'EICAR-Test-File'},
    u'Sophos': {u'result': u'EICAR-AV-Test'},
    u'McAfeeVSCL': {u'result': None},
    u'Symantec': {u'result': u'EICAR Test String'},
    u'StaticAnalyzer': {u'result_code': 1}
    }


##############################################################################
# Test Cases
##############################################################################
class FunctionnalTestCase(unittest.TestCase):
    def setUp(self):
        # setup test
        cwd = os.path.abspath(os.path.dirname(__file__))
        self.filename = "{0}/{1}".format(cwd, EICAR_NAME)
        assert os.path.exists(self.filename)

    def tearDown(self):
        # do the teardown
        pass

    def _test_scan_eicar_file(self,
                              force=False,
                              probe=EICAR_RESULTS.keys(),
                              timeout=SCAN_TIMEOUT_SEC):
        self.scanid = _scan_new(DEBUG)
        self.assertIsNotNone(self.scanid)

        _scan_add(self.scanid, [self.filename], DEBUG)
        probelaunched = _scan_launch(self.scanid, force, probe, DEBUG)
        self.assertEquals(sorted(probelaunched), sorted(probe))
        start = time.time()
        while True:
            (status, _, total, _) = _scan_progress(self.scanid, DEBUG)
            if status == IrmaScanStatus.label[IrmaScanStatus.finished]:
                break
            if status == IrmaScanStatus.label[IrmaScanStatus.launched]:
                self.assertEquals(total, len(probelaunched))
            now = time.time()
            self.assertLessEqual(now, start + timeout, "Results Timeout")
            time.sleep(BEFORE_NEXT_PROGRESS)
        results = _scan_result(self.scanid, DEBUG)
        self.assertEquals(results.keys(), [EICAR_HASH])
        ref_keys = results[EICAR_HASH]['results'].keys()
        self.assertEquals(sorted(ref_keys), sorted(probelaunched))
        for p in probelaunched:
            res = results[EICAR_HASH]['results'][p]['result']
            self.assertEquals(res, EICAR_RESULTS[p]['result'])
        return

    def assertListContains(self, list1, list2):
        for l in list1:
            self.assertIn(l, list2)


class IrmaEicarTest(FunctionnalTestCase):

    def test_get_probe_list(self):
        probelist = _probe_list(DEBUG)
        self.assertEqual(type(probelist), list)
        return

    def test_scan_kaspersky(self):
        self._test_scan_eicar_file(force=True, probe=["Kaspersky"])

    def test_scan_sophos(self):
        self._test_scan_eicar_file(force=True, probe=["Sophos"])

    def test_scan_mcafee(self):
        self._test_scan_eicar_file(force=True, probe=["McAfeeVSCL"])

    def test_scan_clamav(self):
        self._test_scan_eicar_file(force=True, probe=["ClamAV"])

    def test_scan_symantec(self):
        self._test_scan_eicar_file(force=True, probe=["Symantec"])

    def test_scan_staticanalyzer(self):
        self._test_scan_eicar_file(force=True, probe=["StaticAnalyzer"])

    def test_scan_virustotal(self):
        self._test_scan_eicar_file(force=True, probe=["VirusTotal"])


class IrmaMonkeyTests(FunctionnalTestCase):

    def test_scan_add_after_launch(self):
        force = True
        probe = None
        timeout = SCAN_TIMEOUT_SEC
        self.scanid = _scan_new(DEBUG)
        _scan_add(self.scanid, [self.filename], DEBUG)
        _scan_launch(self.scanid, force, probe, DEBUG)
        start = time.time()
        while True:
            (status, _, _, _) = _scan_progress(self.scanid, DEBUG)
            if status == IrmaScanStatus.label[IrmaScanStatus.finished]:
                break
            if status == IrmaScanStatus.label[IrmaScanStatus.launched]:
                with self.assertRaises(IrmaError):
                    _scan_add(self.scanid, [self.filename], DEBUG)
            now = time.time()
            self.assertLessEqual(now, start + timeout, "Results Timeout")
            time.sleep(BEFORE_NEXT_PROGRESS)
        _scan_result(self.scanid, DEBUG)
        with self.assertRaises(IrmaError):
            _scan_add(self.scanid, [self.filename], DEBUG)
        return

    def test_scan_add_after_cancel_new(self):
        self.scanid = _scan_new(DEBUG)
        with self.assertRaises(IrmaError):
            _scan_cancel(self.scanid)
        with self.assertRaises(IrmaError):
            _scan_add(self.scanid, [self.filename], DEBUG)
        return

    def test_scan_add_after_cancel_add(self):
        self.scanid = _scan_new(DEBUG)
        _scan_add(self.scanid, [self.filename], DEBUG)
        with self.assertRaises(IrmaError):
            _scan_cancel(self.scanid)
        with self.assertRaises(IrmaError):
            _scan_add(self.scanid, [self.filename], DEBUG)
        return

    def test_scan_add_after_cancel_launch(self):
        force = False
        probe = None
        self.scanid = _scan_new(DEBUG)
        _scan_add(self.scanid, [self.filename], DEBUG)
        _scan_launch(self.scanid, force, probe, DEBUG)
        with self.assertRaises(IrmaError):
            _scan_cancel(self.scanid)
        with self.assertRaises(IrmaError):
            _scan_add(self.scanid, [self.filename], DEBUG)
        return

    def test_scan_add_after_cancel_results(self):
        self._test_scan_eicar_file(force=False)
        with self.assertRaises(IrmaError):
            _scan_add(self.scanid, [self.filename], DEBUG)
        return


if __name__ == '__main__':
    unittest.main()
