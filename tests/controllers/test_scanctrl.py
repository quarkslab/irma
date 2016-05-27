from unittest import TestCase
from mock import MagicMock, patch

import frontend.controllers.scanctrl as module
from lib.irma.common.utils import IrmaScanStatus
from tempfile import TemporaryFile
from lib.irma.common.exceptions import IrmaValueError, IrmaTaskError
from lib.irma.common.utils import IrmaReturnCode


class TestModuleScanctrl(TestCase):

    def setUp(self):
        self.old_File = module.File
        self.old_build_sha256_path = module.build_sha256_path
        self.old_celery_brain = module.celery_brain
        self.File = MagicMock()
        self.build_sha256_path = MagicMock()
        self.celery_brain = MagicMock()
        module.File = self.File
        module.build_sha256_path = self.build_sha256_path
        module.celery_brain = self.celery_brain

    def tearDown(self):
        module.File = self.old_File
        module.build_sha256_path = self.old_build_sha256_path
        module.celery_brain = self.old_celery_brain
        del self.File
        del self.build_sha256_path
        del self.celery_brain

    def test001_add_files(self):
        fobj = TemporaryFile()
        filename = "n_test"
        scan, session = MagicMock(), MagicMock()
        function = "frontend.controllers.scanctrl.IrmaScanStatus.filter_status"
        with patch(function) as mock:
            module.add_files(scan, {filename: fobj}, session)
        self.assertTrue(mock.called)
        self.assertEqual(mock.call_args,
                         ((scan.status, IrmaScanStatus.empty,
                           IrmaScanStatus.ready),))
        self.File.load_from_sha256.assert_called_once()
        self.build_sha256_path.assert_called_once()
        fobj.close()

    def test002_check_probe(self):
        scan, session = MagicMock(), MagicMock()
        scan.status = IrmaScanStatus.ready
        probelist = ['probe1', 'probe2']
        all_probelist = ['probe1', 'probe2', 'probe3']
        scan.set_probelist.return_value = None
        self.celery_brain.probe_list.return_value = all_probelist
        module.check_probe(scan, probelist, session)
        self.assertTrue(scan.set_probelist.called)
        scan.set_probelist.assert_called_once_with(probelist)

    def test003_check_probe_None(self):
        scan, session = MagicMock(), MagicMock()
        scan.status = IrmaScanStatus.ready
        probelist = None
        all_probelist = ['probe1', 'probe2', 'probe3']
        scan.set_probelist.return_value = None
        self.celery_brain.probe_list.return_value = all_probelist
        module.check_probe(scan, probelist, session)
        self.assertTrue(scan.set_probelist.called)
        scan.set_probelist.assert_called_once_with(all_probelist)

    def test004_check_probe_unknown_probe(self):
        scan, session = MagicMock(), MagicMock()
        scan.status = IrmaScanStatus.ready
        probelist = ['probe1', 'probe2', 'probe6']
        all_probelist = ['probe1', 'probe2', 'probe3']
        scan.set_probelist.return_value = None
        self.celery_brain.probe_list.return_value = all_probelist
        with self.assertRaises(IrmaValueError) as context:
            module.check_probe(scan, probelist, session)
        self.assertFalse(scan.set_probelist.called)
        self.assertEquals(str(context.exception), "probe probe6 unknown")

    def test005_cancel_status_empty(self):
        scan, session = MagicMock(), MagicMock()
        scan.status = IrmaScanStatus.empty
        res = module.cancel(scan, session)
        self.assertIsNone(res)
        scan.set_status.assert_called_once_with(IrmaScanStatus.cancelled)

    def test006_cancel_status_ready(self):
        scan, session = MagicMock(), MagicMock()
        scan.status = IrmaScanStatus.ready
        res = module.cancel(scan, session)
        self.assertIsNone(res)
        scan.set_status.assert_called_once_with(IrmaScanStatus.cancelled)

    def test007_cancel_status_uploaded(self):
        scan, session = MagicMock(), MagicMock()
        scan.status = IrmaScanStatus.uploaded
        label = IrmaScanStatus.label[scan.status]
        expected = "can not cancel scan in {} status".format(label)
        with self.assertRaises(IrmaValueError) as context:
            module.cancel(scan, session)
        self.assertEqual(str(context.exception), expected)

    def test008_cancel_status_launched_ok(self):
        scan, session = MagicMock(), MagicMock()
        scan.status = IrmaScanStatus.launched
        retcode = IrmaReturnCode.success
        cancel_res = {'cancel_details': "details"}
        self.celery_brain.scan_cancel.return_value = (retcode, cancel_res)
        res = module.cancel(scan, session)
        self.assertEqual(res, cancel_res['cancel_details'])
        scan.set_status.assert_called_once_with(IrmaScanStatus.cancelled)

    def test008_cancel_status_launched_status_processed(self):
        scan, session = MagicMock(), MagicMock()
        scan.status = IrmaScanStatus.launched
        retcode = IrmaReturnCode.success
        status = IrmaScanStatus.label[IrmaScanStatus.processed]
        cancel_res = {'status': status}
        self.celery_brain.scan_cancel.return_value = (retcode, cancel_res)
        with self.assertRaises(IrmaValueError) as context:
            module.cancel(scan, session)
        self.assertEqual(str(context.exception),
                         "can not cancel scan in {0} status".format(status))
        scan.set_status.assert_called_once_with(IrmaScanStatus.processed)

    def test008_cancel_status_launched_status_error(self):
        scan, session = MagicMock(), MagicMock()
        scan.status = IrmaScanStatus.error_ftp_upload
        res = module.cancel(scan, session)
        self.assertIsNone(res)
        scan.set_status.assert_not_called()

    def test008_cancel_status_launched_brain_error(self):
        scan, session = MagicMock(), MagicMock()
        scan.status = IrmaScanStatus.launched
        retcode = IrmaReturnCode.error
        ret_val = "reason"
        self.celery_brain.scan_cancel.return_value = (retcode, ret_val)
        with self.assertRaises(IrmaTaskError) as context:
            module.cancel(scan, session)
        self.assertEqual(str(context.exception),
                         ret_val)
        scan.set_status.assert_not_called()

    def test009_cancel_status_processed(self):
        scan, session = MagicMock(), MagicMock()
        scan.status = IrmaScanStatus.processed
        label = IrmaScanStatus.label[scan.status]
        expected = "can not cancel scan in {} status".format(label)
        with self.assertRaises(IrmaValueError) as context:
            module.cancel(scan, session)
        self.assertEqual(str(context.exception), expected)

    def test010_cancel_status_flushed(self):
        scan, session = MagicMock(), MagicMock()
        scan.status = IrmaScanStatus.flushed
        label = IrmaScanStatus.label[scan.status]
        expected = "can not cancel scan in {} status".format(label)
        with self.assertRaises(IrmaValueError) as context:
            module.cancel(scan, session)
        self.assertEqual(str(context.exception), expected)

    def test011_cancel_status_cancelling(self):
        scan, session = MagicMock(), MagicMock()
        scan.status = IrmaScanStatus.cancelling
        label = IrmaScanStatus.label[scan.status]
        expected = "can not cancel scan in {} status".format(label)
        with self.assertRaises(IrmaValueError) as context:
            module.cancel(scan, session)
        self.assertEqual(str(context.exception), expected)

    def test012_cancel_status_cancelled(self):
        scan, session = MagicMock(), MagicMock()
        scan.status = IrmaScanStatus.cancelled
        label = IrmaScanStatus.label[scan.status]
        expected = "can not cancel scan in {} status".format(label)
        with self.assertRaises(IrmaValueError) as context:
            module.cancel(scan, session)
        self.assertEqual(str(context.exception), expected)
