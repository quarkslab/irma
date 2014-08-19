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

import sys
import os
pardir = os.path.abspath(os.path.join(__file__, os.path.pardir))
sys.path.append(os.path.dirname(pardir))

from config.parser import frontend_config
from lib.irma.common.exceptions import IrmaTaskError
from lib.irma.database.sqlhandler import SQLDatabase
import logging
import unittest
# Test config
cwd = os.path.abspath(os.path.dirname(__file__))
os.environ['IRMA_FRONTEND_CFG_PATH'] = cwd


from lib.irma.common.utils import IrmaReturnCode, IrmaScanStatus, \
    IrmaProbeResultsStates
from lib.common.compat import timestamp


from frontend.nosqlobjects import ProbeRealResult
from frontend.sqlobjects import ProbeResult
import frontend.web.core as core
from frontend.web.core import IrmaFrontendWarning, IrmaFrontendError
from frontend.sqlobjects import Scan, sql_db_connect

# Parameter for scan test
PROBES = ['Probe1', 'Probe2']
NB_FILES = 5
FILES = {'file1.bin': 'This is File1 binary data',
         'file2.exe': 'This is File2 binary data',
         'file3.dat': 'This is File3 binary data',
         'file4.scr': 'This is File4 binary data',
         'file5.sys': 'This is File5 binary data'
         }

# ==================
#  Mock Celery tasks
# ==================


def mock_probe_list(successful=True):
    if successful:
        return PROBES
    else:
        raise IrmaFrontendError("Celery timeout - probe_list")


def mock_scan_cancel(scanid, successful=True):
    if successful:
        return (IrmaReturnCode.success, {"total": NB_FILES,
                                         "finished": NB_FILES - 2,
                                         "cancelled": 2})
    else:
        return (IrmaReturnCode.warning, IrmaScanStatus.created)


def mock_scan_launch(scanid, force, successful=True):
    sql_db_connect()
    session = SQLDatabase.get_session()
    scan = Scan.load_from_ext_id(scanid, session)
    if scan.status == IrmaScanStatus.created:
        scan.status = IrmaScanStatus.launched
        scan.update(['status'], session=session)
        session.commit()
        return PROBES
    else:
        raise IrmaTaskError('Not launchable')


def mock_scan_progress(scanid, successful=True):
    if successful:
        return {"total": NB_FILES, "finished": 2, "successful": 2}
    else:
        raise IrmaFrontendWarning(IrmaScanStatus.created)

core._task_probe_list = mock_probe_list
core._task_scan_cancel = mock_scan_cancel
core._task_scan_launch = mock_scan_launch
core._task_scan_progress = mock_scan_progress


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

class WebCoreTestCase(unittest.TestCase):
    def setUp(self):
        sql_db_connect()
        self.session = SQLDatabase.get_session()

    def tearDown(self):
        self.session.commit()

    def assertListContains(self, list1, list2):
        for l in list1:
            self.assertIn(l, list2)


def add_fake_results(scan, probe, session):
    for fw in scan.files_web:
        fw.file.timestamp_last_scan = timestamp()
        fw.file.update(['timestamp_last_scan'], session=session)

        fake_res = 'FAKE-{0}'.format(timestamp())
        """
        # RefResults update
        print "Looking for probe {0} on file {1}".format(probe, fw.file.sha256)
        for rr in fw.file.ref_results:
            print "Found probe {0}".format(rr.probe_name)
        rr = filter(lambda x: x.probe_name == probe, fw.file.ref_results)
        if len(rr) == 0:
            pass
        elif len(rr) == 1:
            rr = rr[0]
            fw.file.ref_results.remove(rr)
        else:
            raise IrmaTaskError("too much refresults found")
        fw.file.ref_results.append({probe: {'result': fake_res}})
        fw.file.update(session=session)
        """
        prr = ProbeRealResult(
            probe_name=probe,
            probe_type=None,
            status=IrmaProbeResultsStates.finished,
            duration=None,
            result=None,
            results=fake_res
        )
        pr = filter(lambda x: x.probe_name == probe, fw.probe_results)
        if len(pr) != 1:
            raise IrmaTaskError("Probe result not found")
        pr = pr[0]
        pr.nosql_id = prr.id
        pr.state = IrmaProbeResultsStates.finished
        pr.update(['nosql_id', 'state'], session=session)
        session.commit()


class TestSQLDatabaseObject(WebCoreTestCase):

    def test_scan_new_id(self):
        # test we got an id
        scanid = core.scan_new()
        self.assertIsNotNone(scanid)

    def test_scan_new_status(self):
        # test we have a correct status
        scanid = core.scan_new()
        scan = Scan.load_from_ext_id(scanid, self.session)

        self.assertIsNotNone(scan.date)
        self.assertEqual(scan.status, IrmaScanStatus.created)
        # self.assertIsNotNone(scan.ip)
        # FIXME scan.is_over with wrong status
        # self.assertFalse(scan.is_over())

    def test_scan_add(self):
        scanid = core.scan_new()
        res = core.scan_add(scanid, FILES)
        self.assertEqual(res, NB_FILES)

        scan = Scan.load_from_ext_id(scanid, self.session)
        self.assertIsNotNone(scan.date)
        self.assertEqual(scan.status, IrmaScanStatus.created)
        self.assertEqual(len(scan.files_web), NB_FILES)
        self.assertEqual(len((scan.files_web[0]).probe_results), 0)
        self.assertFalse(scan.is_over())

    def test_scan_launch(self):
        scanid = core.scan_new()
        self.assertEqual(core.scan_add(scanid, FILES), len(FILES))
        self.assertEqual(core.scan_launch(scanid, True, None),
                         PROBES)
        scan = Scan.load_from_ext_id(scanid, self.session)
        self.assertIsNotNone(scan.date)
        self.assertEqual(scan.status, IrmaScanStatus.launched)
        self.assertEqual(len(scan.files_web), NB_FILES)
        self.assertEqual(len((scan.files_web[0]).probe_results), len(PROBES))
        self.assertFalse(scan.is_over())
        for fw in scan.files_web:
            probelist = [pr.probe_name for pr in fw.probe_results]
            self.assertListContains(PROBES, probelist)
        self.assertFalse(scan.is_over())

    def test_scan_partial_results(self):
        scanid = core.scan_new()
        self.assertEqual(core.scan_add(scanid, FILES), len(FILES))
        self.assertEqual(core.scan_launch(scanid, True, None),
                         PROBES)
        scan = Scan.load_from_ext_id(scanid, self.session)
        self.assertEqual(scan.status, IrmaScanStatus.launched)
        # add fake results to scan
        add_fake_results(scan, PROBES[0], self.session)
        self.assertFalse(scan.is_over())
        results = core.scan_result(scanid)
        self.assertEqual(type(results), dict)
        self.assertEqual(len(results.keys()), NB_FILES)

    def test_scan_full_results(self):
        scanid = core.scan_new()
        self.assertEqual(core.scan_add(scanid, FILES), len(FILES))
        self.assertEqual(core.scan_launch(scanid, True, None),
                         PROBES)
        scan = Scan.load_from_ext_id(scanid, self.session)
        self.assertEqual(scan.status, IrmaScanStatus.launched)
        # add all fake results to scan
        for p in PROBES:
            add_fake_results(scan, p, self.session)

        results = core.scan_result(scanid)
        self.assertEqual(type(results), dict)
        self.assertEqual(len(results.keys()), NB_FILES)
        for (_, res_dict) in results.items():
            self.assertEqual(len(res_dict['results']), len(PROBES))
        self.assertTrue(scan.is_over())

if __name__ == '__main__':
    enable_logging()
    unittest.main()
