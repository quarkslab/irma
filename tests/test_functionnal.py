import unittest, os, random
from frontend.cli.irma import _ping, _scan_new, _scan_add, _probe_list, _scan_launch, _scan_progress, IrmaScanStatus, \
    _scan_result
import time

SCAN_TIMEOUT_SEC = 300
BEFORE_NEXT_PROGRESS = 5
DEBUG = True
EICAR_NAME = "eicar.com"
EICAR_HASH = u'275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f'
EICAR_RESULTS = {
           u'nsrl': {u'result': [u'eicar.com.txt,68,18115,358,']},
           u'clamav': {u'version': u'ClamAV 0.97.8/18526/Sat Mar  1 22:54:55 2014', u'result': u'Eicar-Test-Signature'},
           u'virustotal': {u'result': u'47/49 positives'},
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
        filename = "{0}/{1}".format(os.path.abspath(os.path.dirname(__file__)), EICAR_NAME)
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
        results = _scan_result(scanid, DEBUG)
        self.assertEquals(type(results), dict)
        self.assertListContains(results.keys(), EICAR_HASH)
        self.assertListContains(results[EICAR_HASH]['results'].keys(), probelaunched)
        for probe in results[EICAR_HASH]['results'].keys():
            self.assertEquals(results[EICAR_HASH]['results'][probe]['result'], EICAR_RESULTS[probe]['result'])
        return

    def test_scan_one_file_forced(self):
        scanid = _scan_new(DEBUG)
        self.assertIsNotNone(scanid)
        filename = "{0}/{1}".format(os.path.abspath(os.path.dirname(__file__)), EICAR_NAME)
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
        results = _scan_result(scanid, DEBUG)
        self.assertEquals(type(results), dict)
        self.assertListContains(results.keys(), EICAR_HASH)
        self.assertListContains(results[EICAR_HASH]['results'].keys(), probelaunched)
        for probe in results[EICAR_HASH]['results'].keys():
            self.assertEquals(results[EICAR_HASH]['results'][probe]['result'], EICAR_RESULTS[probe]['result'])
        return

    def test_scan_one_probe(self):
        probelist = [probe for probe in _probe_list(DEBUG) if probe in EICAR_RESULTS.keys()]
        probeselected = probelist[random.randrange(len(probelist))]
        scanid = _scan_new(DEBUG)
        self.assertIsNotNone(scanid)
        filename = "{0}/{1}".format(os.path.abspath(os.path.dirname(__file__)), EICAR_NAME)
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
        results = _scan_result(scanid, DEBUG)
        self.assertEquals(type(results), dict)
        self.assertListContains(results.keys(), EICAR_HASH)
        self.assertListContains(results[EICAR_HASH]['results'].keys(), probelaunched)
        for probe in results[EICAR_HASH]['results'].keys():
            self.assertEquals(results[EICAR_HASH]['results'][probe]['result'], EICAR_RESULTS[probe]['result'])
        return

if __name__ == '__main__':
    unittest.main()
