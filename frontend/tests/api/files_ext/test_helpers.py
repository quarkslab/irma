from unittest import TestCase
from mock import MagicMock
import api.files_ext.helpers as module
import api.files_ext.models as models


class TestFileExtHelpers(TestCase):

    def test_new_file_ext1(self):
        file = MagicMock()
        filename = "/path/foo"
        payload = MagicMock()
        res = module.new_file_ext("webui", file,
                                  filename, payload)
        self.assertEqual(res.submitter_type, models.FileWeb.submitter_type)
        self.assertEqual(res.file, file)
        self.assertEqual(res.name, filename)
        self.assertEqual(res.depth, 0)

    def test_new_file_ext2(self):
        file = MagicMock()
        filename = "/path/foo"
        payload = MagicMock()
        res = module.new_file_ext("cli", file,
                                  filename, payload)
        self.assertEqual(res.submitter_type, models.FileCli.submitter_type)
        self.assertEqual(res.file, file)
        self.assertEqual(res.depth, 0)

    def test_new_file_ext3(self):
        file = MagicMock()
        filename = "/path/foo"
        payload = MagicMock()
        res = module.new_file_ext("kiosk", file,
                                  filename, payload)
        self.assertEqual(res.submitter_type, models.FileKiosk.submitter_type)
        self.assertEqual(res.file, file)
        self.assertEqual(res.depth, 0)

    def test_new_file_ext4(self):
        file = MagicMock()
        filename = "/path/foo"
        payload = MagicMock()
        res = module.new_file_ext("suricata", file,
                                  filename, payload)
        self.assertEqual(res.submitter_type,
                         models.FileSuricata.submitter_type)
        self.assertEqual(res.file, file)
        self.assertEqual(res.context, payload)
        self.assertEqual(res.depth, 0)

    def test_new_file_ext_unknown(self):
        file = MagicMock()
        filename = "/path/foo"
        payload = MagicMock()
        with self.assertRaises(ValueError):
            module.new_file_ext("undefined", file, filename, payload)
