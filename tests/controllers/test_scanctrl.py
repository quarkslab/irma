#
# Copyright (c) 2013-2016 Quarkslab.
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

from unittest import TestCase
from mock import MagicMock, patch
from random import randint, choice, shuffle

from lib.irma.common.utils import IrmaScanStatus
import brain.controllers.scanctrl as module

from brain.models.sqlobjects import Scan, User
from lib.irma.common.exceptions import IrmaDatabaseResultNotFound


# ============
#  Test cases
# ============

class TestScanctrl(TestCase):

    def setUp(self):
        self.session = MagicMock()
        self.name = "user"
        self.rmqvhost = "vhost"
        self.ftpuser = "ftpuser"
        self.user = User(self.name,
                         self.rmqvhost,
                         self.ftpuser)
        self.frontend_scanid = "frontend_scanid"
        self.nb_files = randint(50, 100)
        self.scan = Scan(frontend_scanid=self.frontend_scanid,
                         user_id=self.user.id,
                         nb_files=self.nb_files)
        self.scan.user = self.user

    def tearDown(self):
        pass

    @patch("brain.controllers.scanctrl.Scan")
    def test001_new_scan_existing(self, m_scan):
        m_scan.get_scan.return_value = self.scan
        old_nb_files = self.scan.nb_files
        new_nb_files = randint(150, 200)
        scan = module.new(self.frontend_scanid, self.user, new_nb_files,
                          self.session)
        self.session.query().filter().update.assert_called()
        m_scan().save.assert_not_called()
        self.assertNotEqual(self.nb_files, new_nb_files)
        self.assertEqual(scan, self.scan)
        self.assertEqual(scan.nb_files, new_nb_files+old_nb_files)

    @patch("brain.controllers.scanctrl.Scan")
    def test002_new_file_not_existing(self, m_scan):
        m_scan.get_scan.side_effect = IrmaDatabaseResultNotFound()
        old_nb_files = self.scan.nb_files
        new_nb_files = randint(150, 200)
        scan = module.new(self.frontend_scanid, self.user, new_nb_files,
                          self.session)
        self.session.query().filter().update.assert_not_called()
        m_scan().save.assert_called()
        self.assertNotEqual(self.nb_files, new_nb_files)
        self.assertEqual(scan.nb_files, m_scan().nb_files)

    def test003_set_status_existing(self):
        self.assertEqual(self.scan.status, IrmaScanStatus.empty)
        status = choice(IrmaScanStatus.label.keys())
        module.set_status(self.scan, status, self.session)
        self.assertEqual(self.scan.status, status)
        self.session.commit.assert_called_once()

    def test004_set_status_not_existing(self):
        self.assertEqual(self.scan.status, IrmaScanStatus.empty)
        status = "whatever"
        with self.assertRaises(ValueError):
            module.set_status(self.scan, status, self.session)
        self.assertEqual(self.scan.status, IrmaScanStatus.empty)
        self.session.commit.assert_not_called()

    def test005_check_probelist(self):
        available_probelist = range(10)
        shuffle(available_probelist)
        probelist = available_probelist[:5]
        old_status = self.scan.status
        module.check_probelist(self.scan, probelist, available_probelist,
                               self.session)
        self.assertEqual(self.scan.status, old_status)

    def test006_check_probelist_None(self):
        available_probelist = range(10)
        probelist = None
        old_status = self.scan.status
        with self.assertRaises(ValueError):
            module.check_probelist(self.scan, probelist,
                                   available_probelist,
                                   self.session)
        self.assertEqual(self.scan.status, IrmaScanStatus.error_probe_missing)

    def test007_check_probelist_unknown_probe(self):
        available_probelist = range(10)
        shuffle(available_probelist)
        probelist = "11"
        old_status = self.scan.status
        with self.assertRaises(ValueError):
            module.check_probelist(self.scan, probelist,
                                   available_probelist,
                                   self.session)
        self.assertEqual(self.scan.status, IrmaScanStatus.error_probe_missing)

    def test008_flush_already_flushed(self):
        self.scan.status = IrmaScanStatus.flushed
        module.flush(self.scan, self.session)
        self.session.delete.assert_not_called()

    @patch("brain.controllers.scanctrl.ftp_ctrl")
    def test009_flush(self, m_ftp_ctrl):
        self.assertNotEqual(self.scan.status, IrmaScanStatus.flushed)
        j1, j2 = MagicMock(), MagicMock()
        self.scan.jobs = [j1, j2]
        module.flush(self.scan, self.session)
        m_ftp_ctrl.flush_dir.assert_called_once_with(self.ftpuser,
                                                     self.frontend_scanid)
        self.session.delete.assert_any_call(j1)
        self.session.delete.assert_any_call(j2)
        self.assertEqual(self.scan.status, IrmaScanStatus.flushed)

    @patch("brain.controllers.scanctrl.celery_probe")
    def test010_scan_launch(self, m_celery_probe):
        j1, j2 = MagicMock(), MagicMock()
        self.scan.jobs = [j1, j2]
        module.launch(self.scan, self.scan.jobs, self.session)
        m_celery_probe.job_launch.assert_any_call(self.ftpuser,
                                                  self.frontend_scanid,
                                                  j1.filehash,
                                                  j1.probename,
                                                  j1.task_id)
        m_celery_probe.job_launch.assert_any_call(self.ftpuser,
                                                  self.frontend_scanid,
                                                  j2.filehash,
                                                  j2.probename,
                                                  j2.task_id)
        self.assertEqual(self.scan.status, IrmaScanStatus.launched)

    @patch("brain.controllers.scanctrl.flush")
    @patch("brain.controllers.scanctrl.celery_probe")
    def test011_scan_cancel(self, m_celery_probe, m_flush):
        j1, j2 = MagicMock(), MagicMock()
        self.scan.jobs = [j1, j2]
        module.cancel(self.scan, self.session)
        m_celery_probe.job_cancel.assert_called_once_with([j1.task_id,
                                                           j2.task_id])
        m_flush.assert_called_once_with(self.scan, self.session)

    @patch("brain.controllers.scanctrl.flush")
    @patch("brain.controllers.scanctrl.celery_probe")
    def test012_scan_cancel_no_jobs(self, m_celery_probe, m_flush):
        self.scan.jobs = []
        module.cancel(self.scan, self.session)
        m_celery_probe.job_cancel.assert_not_called()
        m_flush.assert_called_once_with(self.scan, self.session)
