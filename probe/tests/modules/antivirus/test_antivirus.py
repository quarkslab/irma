import os
import unittest
from mock import patch, MagicMock
import modules.antivirus.base as base
from pathlib import Path


def set_win_environ():
    os.environ['PROGRAMDATA'] = "C:\\ProgramData"
    os.environ['PROGRAMFILES'] = "C:\\Program Files"
    os.environ['PROGRAMFILES(X86)'] = "C:\\Program Files (x86)"


class AbstractTests(object):
    class TestAntivirus(unittest.TestCase):
        name = "unavailable"
        database = ["/a/first/database", "/a/second/database"]
        scan_args = ()
        scan_path = None
        version = "unavailable"
        version_stdout = None
        virus_database_version = "unavailable"
        virus_database_version_stdout = ""
        path = None
        module = None
        locate_res = None
        filename = "eicar.com.txt"
        virusname = "VirusName"
        scan_clean_retcode = 0
        scan_clean_stdout = None
        scan_virus_retcode = 1
        scan_virus_stdout = None

        def setUp(self):
            self.plugin = self.module()

        def test_attributes(self):
            self.assertEquals(self.plugin.scan_path, self.scan_path)
            self.assertEquals(self.plugin.version, self.version)
            self.assertEquals(self.plugin.name, self.name)
            self.assertEquals(self.plugin.database, self.database)
            self.assertEquals(self.plugin.virus_database_version,
                              self.virus_database_version)

        @patch.object(base.Antivirus, "run_cmd")
        def test_scan_clean(self, m_run_cmd):
            file = MagicMock()
            retcode = self.scan_clean_retcode
            stderr = ""
            m_run_cmd.return_value = retcode, self.scan_clean_stdout, stderr
            res = self.plugin.scan(file)
            m_run_cmd.assert_called_with(self.plugin.scan_path,
                                         *self.scan_args,
                                         file, env=None)
            self.assertEquals(res, 0)
            self.assertIsNone(self.plugin.scan_results[file])

        @patch.object(base.Antivirus, "identify_threat")
        @patch.object(base.Antivirus, "run_cmd")
        def test_scan_virus(self, m_run_cmd, m_identify_threat):
            file = MagicMock()
            retcode = self.scan_virus_retcode
            stderr = ""
            m_run_cmd.return_value = retcode, self.scan_virus_stdout, stderr
            m_identify_threat.return_value = self.virusname
            res = self.plugin.scan(file)
            m_run_cmd.assert_called_with(self.plugin.scan_path,
                                         *self.scan_args,
                                         file, env=None)
            self.assertEquals(res, 1)
            self.assertEquals(self.plugin.scan_results[file], self.virusname)

        def test_identify_threat_virus(self):
            res = self.plugin.identify_threat(Path(self.filename),
                                              str(self.scan_virus_stdout))
            self.assertEquals(res, self.virusname)

        def test_identify_threat_clean(self):
            res = self.plugin.identify_threat(Path(self.filename),
                                              str(self.scan_clean_stdout))
            self.assertIsNone(res)
