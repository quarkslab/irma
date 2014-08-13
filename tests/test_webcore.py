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
from lib.irma.database.sqlhandler import SQLDatabase

pardir = os.path.abspath(os.path.join(__file__, os.path.pardir))
sys.path.append(os.path.dirname(pardir))

import logging
import unittest
from lib.irma.common.utils import IrmaReturnCode, IrmaScanStatus
from lib.irma.common.exceptions import IrmaConfigurationError
from lib.common.compat import timestamp

# Test config
cwd = os.path.abspath(os.path.dirname(__file__))
os.environ['IRMA_FRONTEND_CFG_PATH'] = cwd

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
    return ['Probe1', 'Probe2']


def mock_scan_progress(scanid, successful=True):
    if successful:
        return {"total": NB_FILES, "finished": 2, "successful": 2}
    else:
        raise IrmaFrontendWarning(IrmaScanStatus.created)


def mock_scan_add_result(scanid):
    sql_db_connect()
    session = SQLDatabase.get_session()
    scan = Scan.load_from_ext_id(scanid, session)
    if scan.status != IrmaScanStatus.launched:
        raise IrmaFrontendWarning(scan.status)


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
        pass

    def assertListContains(self, list1, list2):
        for l in list1:
            self.assertIn(l, list2)


def add_fake_results(scan, probe):
    for (scanfile_id, scanres_id) in scan.scanfile_ids.items():
        scanfile = ScanFile(id=scanfile_id, mode=IrmaLockMode.write)
        scanfile.date_last_scan = timestamp()
        scanfile.update()
        scanfile.release()

        fake_res = 'FAKE-{0}'.format(timestamp())
        scanrefres = ScanRefResults.init_id(scanfile.id)
        scanrefres.results[probe] = {'result': fake_res}
        scanrefres.update()
        scanrefres.release()

        scanres = ScanResults(id=scanres_id)
        scanres.take()
        scanres.results[probe] = {'result': fake_res}
        scanres.update()
        scanres.release()


class TestSQLDatabaseObject(WebCoreTestCase):

    def test_scan_new_id(self):
        # test we got an id
        scanid = core.scan_new()
        self.assertIsNotNone(scanid)

    def test_scan_new_status(self):
        # test we have a correct status
        scanid = core.scan_new()
        scan = ScanInfo(id=scanid)

        self.assertIsNotNone(scan.date)
        self.assertEqual(type(scan.scanfile_ids), dict)
        self.assertEqual(len(scan.scanfile_ids), 0)
        self.assertIsNone(scan.probelist)
        self.assertEqual(scan.status, IrmaScanStatus.created)
        # FIXME scan.is_completed with wrong status
        # self.assertFalse(scan.is_completed())

    def test_scan_add(self):
        scanid = core.scan_new()
        res = core.scan_add(scanid, FILES)
        self.assertEqual(res, NB_FILES)

        scan = ScanInfo(id=scanid)
        self.assertIsNotNone(scan.date)
        self.assertEqual(type(scan.scanfile_ids), dict)
        self.assertEqual(len(scan.scanfile_ids), NB_FILES)
        self.assertIsNone(scan.probelist)
        self.assertEqual(scan.status, IrmaScanStatus.created)
        # FIXME scan.probelist should be init with [] instead of None
        # to fix for loop in is_completed
        # self.assertFalse(scan.is_completed())

    def test_scan_launch(self):
        scanid = core.scan_new()
        self.assertEqual(core.scan_add(scanid, FILES), len(FILES))
        self.assertEqual(core.scan_launch(scanid, True, None),
                         PROBES)
        scan = ScanInfo(id=scanid)
        self.assertIsNotNone(scan.date)
        self.assertEqual(type(scan.scanfile_ids), dict)
        self.assertEqual(len(scan.scanfile_ids), NB_FILES)
        self.assertEqual(type(scan.probelist), list)
        self.assertEqual(len(scan.probelist), len(PROBES))
        self.assertEqual(scan.status, IrmaScanStatus.launched)
        self.assertFalse(scan.is_completed())
        self.assertListContains(PROBES, scan.probelist)
        self.assertFalse(scan.is_completed())

    def test_scan_partial_results(self):
        scanid = core.scan_new()
        self.assertEqual(core.scan_add(scanid, FILES), len(FILES))
        self.assertEqual(core.scan_launch(scanid, True, None),
                         PROBES)
        scan = ScanInfo(id=scanid)
        # add fake results to scan
        add_fake_results(scan, PROBES[0])
        self.assertFalse(scan.is_completed())
        results = scan.get_results(None)
        self.assertEqual(type(results), dict)
        self.assertEqual(len(results.keys()), NB_FILES)

    def test_scan_full_results(self):
        scanid = core.scan_new()
        self.assertEqual(core.scan_add(scanid, FILES), len(FILES))
        self.assertEqual(core.scan_launch(scanid, True, None),
                         PROBES)
        scan = ScanInfo(id=scanid)
        # add fake results to scan
        for p in PROBES:
            add_fake_results(scan, p)
        self.assertTrue(scan.is_completed())
        results = scan.get_results(None)
        self.assertEqual(type(results), dict)
        self.assertEqual(len(results.keys()), NB_FILES)
        for (_, res_dict) in results.items():
            self.assertEqual(len(res_dict['results']), len(PROBES))

if __name__ == '__main__':
    enable_logging()
    unittest.main()
