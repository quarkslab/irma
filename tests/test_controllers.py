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
from random import shuffle
pardir = os.path.abspath(os.path.join(__file__, os.path.pardir))
sys.path.append(os.path.dirname(pardir))

import logging
import unittest
# Test config
cwd = os.path.abspath(os.path.dirname(__file__))
os.environ['IRMA_BRAIN_CFG_PATH'] = cwd
from brain.helpers.sql import session_query, session_transaction


from lib.irma.common.utils import IrmaScanStatus
from lib.common.utils import UUID
from lib.common.compat import timestamp

import brain.controllers.scanctrl as scan_ctrl
import brain.controllers.userctrl as user_ctrl
from brain.models.sqlobjects import Scan, User
from lib.irma.common.exceptions import IrmaValueError, IrmaTaskError, \
    IrmaDatabaseError, IrmaDatabaseResultNotFound


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
        self.user_name = "test_user"
        self.user_rmqvhost = "test_vhost"
        self.user_ftpuser = "test_ftpuser"
        self.user_quota = 100
        self.scanid = UUID.generate()
        try:
            self.userid = user_ctrl.get_userid(self.user_rmqvhost)
        except IrmaDatabaseResultNotFound:
            # user does not exist create one
            with session_transaction() as session:
                user = User(self.user_name,
                            self.user_rmqvhost,
                            self.user_ftpuser,
                            self.user_quota)
                user.save(session)
                self.userid = user.id

    def tearDown(self):
        pass


class TestScanController(scanctrlTestCase):
    # ======
    #  SCAN
    # ======
    def test_scan_new_id(self):
        # test we got an id
        scanid = scan_ctrl.new(self.scanid, self.userid, 0)
        self.assertIsNotNone(scanid)

    def test_scan_new_status(self):
        # test we have corrects fields
        scanid = scan_ctrl.new(self.scanid, self.userid, 10)
        with session_query() as session:
            scan = Scan.load(scanid, session)
            self.assertIsNotNone(scan.timestamp)
            self.assertEqual(scan.status, IrmaScanStatus.empty)
            self.assertEqual(scan.nb_files, 10)
            self.assertIsNotNone(scan.nb_jobs)

    def test_scan_launched(self):
        scan_id = scan_ctrl.new(self.scanid, self.userid, 10)
        for i in xrange(0, 10):
            for probe in ['probe1', 'probe2']:
                scan_ctrl.job_new(scan_id, "file-{0}".format(i), probe)
        scan_ctrl.launched(scan_id)
        with session_query() as session:
            scan = Scan.load(scan_id, session)
            self.assertEqual(scan.status, IrmaScanStatus.launched)
            self.assertEqual(scan.nb_files, 10)
            self.assertEqual(scan.nb_jobs, 20)

    def test_scan_error(self):
        scanid = scan_ctrl.new(self.scanid, self.userid, 10)
        for code in IrmaScanStatus.label.keys():
            scan_ctrl.error(scanid, code)
            with session_query() as session:
                scan = Scan.load(scanid, session)
                self.assertEqual(scan.status, code)

    def test_scan_job_success(self):
        scan_id = scan_ctrl.new(self.scanid, self.userid, 10)
        job_ids = []
        for i in xrange(0, 10):
            for probe in ['probe1', 'probe2']:
                job_ids.append(scan_ctrl.job_new(scan_id,
                                                 "file-{0}".format(i),
                                                 probe))
        scan_ctrl.launched(scan_id)
        shuffle(job_ids)
        for job_id in job_ids:
            scan_ctrl.job_success(job_id)
        self.assertTrue(scan_ctrl.check_finished(scan_id))
        with session_query() as session:
            scan = Scan.load(scan_id, session)
            self.assertEqual(scan.status, IrmaScanStatus.processed)
            self.assertEqual(scan.nb_files, 10)
            self.assertEqual(scan.nb_jobs, 20)

    def test_scan_job_error(self):
        scan_id = scan_ctrl.new(self.scanid, self.userid, 10)
        job_ids = []
        for i in xrange(0, 10):
            for probe in ['probe1', 'probe2']:
                job_ids.append(scan_ctrl.job_new(scan_id,
                                                 "file-{0}".format(i),
                                                 probe))
        scan_ctrl.launched(scan_id)
        shuffle(job_ids)
        for job_id in job_ids:
            scan_ctrl.job_error(job_id)
        self.assertTrue(scan_ctrl.check_finished(scan_id))
        with session_query() as session:
            scan = Scan.load(scan_id, session)
            self.assertEqual(scan.status, IrmaScanStatus.processed)
            self.assertEqual(scan.nb_files, 10)
            self.assertEqual(scan.nb_jobs, 20)

    def test_scan_progress(self):
        scan_id = scan_ctrl.new(self.scanid, self.userid, 10)
        job_ids = []
        for i in xrange(0, 10):
            for probe in ['probe1', 'probe2']:
                job_ids.append(scan_ctrl.job_new(scan_id,
                                                 "file-{0}".format(i),
                                                 probe))
        scan_ctrl.launched(scan_id)
        shuffle(job_ids)
        for i, job_id in enumerate(job_ids[:-1]):
            scan_ctrl.job_success(job_id)
            (status, progress_details) = scan_ctrl.progress(scan_id)
            self.assertEqual(status,
                             IrmaScanStatus.label[IrmaScanStatus.launched])
            self.assertIsNotNone(progress_details)
            self.assertEqual(progress_details['successful'], i + 1)

    def test_scan_cancel(self):
        scanid = scan_ctrl.new(self.scanid, self.userid, 10)
        for code in IrmaScanStatus.label.keys():
            scan_ctrl.error(scanid, code)
            with session_query() as session:
                scan = Scan.load(scanid, session)
                self.assertEqual(scan.status, code)


class TestUserController(scanctrlTestCase):

    def test_user_quota(self):
        # test we have a correct quota
        (remaining, quota) = user_ctrl.get_quota(self.userid)
        self.assertIsNotNone(quota)
        self.assertEqual(type(quota), int)
        self.assertIsNotNone(remaining)
        self.assertEqual(type(remaining), int)

    def test_user_quota_update(self):
        # test update quota
        (before, _) = user_ctrl.get_quota(self.userid)
        scanid = scan_ctrl.new(self.scanid, self.userid, 2)
        for i in xrange(0, 10):
            for probe in ['probe1', 'probe2']:
                scan_ctrl.job_new(scanid, "file-{0}".format(i), probe)
        scan_ctrl.launched(scanid)
        (after, _) = user_ctrl.get_quota(self.userid)
        self.assertEqual(before - after, 20)
        with session_query() as session:
            user = User.load(self.userid, session)
            scan_ids = [scan.id for scan in user.scans]
            self.assertNotEqual(scan_ids, [])
            self.assertTrue(scanid in scan_ids)

if __name__ == '__main__':
    enable_logging()
    unittest.main()
