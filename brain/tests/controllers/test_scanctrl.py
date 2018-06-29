#
# Copyright (c) 2013-2018 Quarkslab.
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
from random import randint, choice

from irma.common.base.utils import IrmaScanStatus
import brain.controllers.scanctrl as module

from brain.models.sqlobjects import Scan, User
from irma.common.base.exceptions import IrmaDatabaseResultNotFound


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
                         user_id=self.user.id)
        self.scan.user = self.user

    def tearDown(self):
        pass

    @patch("brain.controllers.scanctrl.Scan")
    def test_new_scan_existing(self, m_scan):
        m_scan.get_scan.return_value = self.scan
        scan = module.new(self.frontend_scanid, self.user, self.session)
        self.session.add.assert_not_called()
        self.assertEqual(scan, self.scan)

    @patch("brain.controllers.scanctrl.Scan")
    def test_new_file_not_existing(self, m_scan):
        m_scan.get_scan.side_effect = IrmaDatabaseResultNotFound()
        module.new(self.frontend_scanid, self.user, self.session)
        self.session.add.assert_called()

    def test_set_status_existing(self):
        self.assertEqual(self.scan.status, IrmaScanStatus.empty)
        status = choice(list(IrmaScanStatus.label.keys()))
        module.set_status(self.scan, status, self.session)
        self.assertEqual(self.scan.status, status)
        self.session.commit.assert_called_once()

    def test_set_status_not_existing(self):
        self.assertEqual(self.scan.status, IrmaScanStatus.empty)
        status = "whatever"
        with self.assertRaises(ValueError):
            module.set_status(self.scan, status, self.session)
        self.assertEqual(self.scan.status, IrmaScanStatus.empty)
        self.session.commit.assert_not_called()

    def test_flush_already_flushed(self):
        self.scan.status = IrmaScanStatus.flushed
        module.flush(self.scan, self.session)
        self.session.delete.assert_not_called()

    @patch("brain.controllers.scanctrl.ftp_ctrl")
    def test_flush(self, m_ftp_ctrl):
        self.assertNotEqual(self.scan.status, IrmaScanStatus.flushed)
        j1, j2 = MagicMock(), MagicMock()
        self.scan.jobs = [j1, j2]
        module.flush(self.scan, self.session)
        m_ftp_ctrl.flush.assert_called_once_with(self.ftpuser,
                                                 self.scan.files)
        self.session.delete.assert_any_call(j1)
        self.session.delete.assert_any_call(j2)
        self.assertEqual(self.scan.status, IrmaScanStatus.flushed)

    @patch("brain.controllers.scanctrl.celery_probe")
    def test_scan_launch(self, m_celery_probe):
        j1, j2 = MagicMock(), MagicMock()
        self.scan.jobs = [j1, j2]
        module.launch(self.scan, self.scan.jobs, self.session)
        m_celery_probe.job_launch.assert_any_call(self.ftpuser,
                                                  j1.filename,
                                                  j1.probename,
                                                  j1.task_id)
        m_celery_probe.job_launch.assert_any_call(self.ftpuser,
                                                  j2.filename,
                                                  j2.probename,
                                                  j2.task_id)
        self.assertEqual(self.scan.status, IrmaScanStatus.launched)

    @patch("brain.controllers.scanctrl.flush")
    @patch("brain.controllers.scanctrl.celery_probe")
    def test_scan_cancel(self, m_celery_probe, m_flush):
        j1, j2 = MagicMock(), MagicMock()
        self.scan.jobs = [j1, j2]
        module.cancel(self.scan, self.session)
        m_celery_probe.job_cancel.assert_called_once_with([j1.task_id,
                                                           j2.task_id])
        m_flush.assert_called_once_with(self.scan, self.session)

    @patch("brain.controllers.scanctrl.flush")
    @patch("brain.controllers.scanctrl.celery_probe")
    def test_scan_cancel_no_jobs(self, m_celery_probe, m_flush):
        self.scan.jobs = []
        module.cancel(self.scan, self.session)
        m_celery_probe.job_cancel.assert_not_called()
        m_flush.assert_called_once_with(self.scan, self.session)
