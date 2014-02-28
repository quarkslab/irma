import unittest, os, random
from frontend.cli.irma import _ping, _scan_new, _scan_add, _probe_list, _scan_launch, _scan_progress, IrmaScanStatus, \
    _scan_results
import time

TEST_NAME = "eicar.com"
SCAN_TIMEOUT_SEC = 60
BEFORE_NEXT_PROGRESS = 5
DEBUG = True

RESULTS = {
           u'nsrl': {u'result': [u'eicar.com.txt,68,18115,358,']},
           u'clamav': {u'version': u'ClamAV 0.97.8/18523/Fri Feb 28 10:59:27 2014', u'result': u'Eicar-Test-Signature'},
           u'virustotal': {u'result': u'48/50 positives'},
           u'kaspersky': {u'version': u'Kaspersky Anti-Virus (R) 14.0.0.4837', u'result': u'EICAR-Test-File'}}

##############################################################################
# Test Cases
##############################################################################
class FunctionnalTestCase(unittest.TestCase):
    def setUp(self):
        # check database is ready for test
        try:
            _ping()
        except:
            self.skipTest(FunctionnalTestCase)

    def tearDown(self):
        # do the teardown
        pass

class IrmaCliTest(FunctionnalTestCase):
    def assertListContains(self, list1, list2):
        for l in list1:
            self.assertIn(l, list2)


    def test_get_probe_list(self):
        probelist = _probe_list(DEBUG)
        self.assertEqual(type(probelist), list)
        return

    def test_scan_one_file(self):
        scanid = _scan_new(DEBUG)
        self.assertIsNotNone(scanid)
        filename = "{0}/{1}".format(os.path.abspath(os.path.dirname(__file__)), TEST_NAME)
        _scan_add(scanid, [filename], DEBUG)
        force = False
        probe = None
        probelaunched = _scan_launch(scanid, force, probe, DEBUG)
        self.assertEquals(type(probelaunched), list)
        start = time.time()
        while True:
            (status , _, total, _) = _scan_progress(scanid, DEBUG)
            if status == IrmaScanStatus.label[IrmaScanStatus.finished]:
                break
            if status == IrmaScanStatus.label[IrmaScanStatus.launched]:
                self.assertEquals(total, len(probelaunched))
            now = time.time()
            self.assertLessEqual(now, start + SCAN_TIMEOUT_SEC, "Results Timeout")
            time.sleep(BEFORE_NEXT_PROGRESS)
        results = _scan_results(scanid, DEBUG)
        self.assertEquals(type(results), dict)
        self.assertListContains(results[TEST_NAME].keys(), probelaunched)
        for probe in results[TEST_NAME].keys():
            self.assertEquals(results[TEST_NAME][probe], RESULTS[probe])
        return

    def test_scan_one_file_forced(self):
        scanid = _scan_new(DEBUG)
        self.assertIsNotNone(scanid)
        filename = "{0}/{1}".format(os.path.abspath(os.path.dirname(__file__)), TEST_NAME)
        _scan_add(scanid, [filename], DEBUG)
        force = True
        probe = None
        probelaunched = _scan_launch(scanid, force, probe, DEBUG)
        self.assertEquals(type(probelaunched), list)
        start = time.time()
        while True:
            (status , _, total, _) = _scan_progress(scanid, DEBUG)
            if status == IrmaScanStatus.label[IrmaScanStatus.finished]:
                break
            if status == IrmaScanStatus.label[IrmaScanStatus.launched]:
                self.assertEquals(total, len(probelaunched))
            now = time.time()
            print "{0} sec elapsed".format(now - start)
            self.assertLessEqual(now, start + SCAN_TIMEOUT_SEC, "Results Timeout")
            time.sleep(BEFORE_NEXT_PROGRESS)
        results = _scan_results(scanid, DEBUG)
        self.assertEquals(type(results), dict)
        self.assertListContains(results[TEST_NAME].keys(), probelaunched)
        for probe in results[TEST_NAME].keys():
            self.assertEquals(results[TEST_NAME][probe], RESULTS[probe])
        return

    def test_scan_one_probe(self):
        probelist = [probe for probe in _probe_list(DEBUG) if probe in RESULTS.keys()]
        probeselected = probelist[random.randrange(len(probelist))]
        scanid = _scan_new(DEBUG)
        self.assertIsNotNone(scanid)
        filename = "{0}/{1}".format(os.path.abspath(os.path.dirname(__file__)), TEST_NAME)
        _scan_add(scanid, [filename], DEBUG)
        force = True
        probe = [probeselected]
        probelaunched = _scan_launch(scanid, force, probe, DEBUG)
        self.assertEquals(probelaunched, [probeselected])
        start = time.time()
        while True:
            (status , _, total, _) = _scan_progress(scanid, DEBUG)
            if status == IrmaScanStatus.label[IrmaScanStatus.finished]:
                break
            if status == IrmaScanStatus.label[IrmaScanStatus.launched]:
                self.assertEquals(total, len(probelaunched))
            now = time.time()
            self.assertLessEqual(now, start + SCAN_TIMEOUT_SEC, "Results Timeout")
            time.sleep(BEFORE_NEXT_PROGRESS)
        results = _scan_results(scanid, DEBUG)
        self.assertEquals(type(results), dict)
        self.assertListContains(probelaunched, results[TEST_NAME].keys())
        for probe in probelaunched:
            self.assertEquals(results[TEST_NAME][probe], RESULTS[probe])
        return

if __name__ == '__main__':
    unittest.main()
