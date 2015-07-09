from unittest import TestCase
import frontend.cli.apiclient as module
import lib.irma.common.utils as reference


class TestModuleApiClient(TestCase):

    def test001_test_all_status_present(self):
        # Check if the copied scan status are
        # all present
        label_ref = reference.IrmaScanStatus.label
        label_copy = module.IrmaScanStatus.label
        self.assertEqual(label_ref, label_copy)
