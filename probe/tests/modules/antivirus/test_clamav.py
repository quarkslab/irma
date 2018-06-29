from .test_antivirus import AbstractTests
import modules.antivirus.clamav.clam as module
import modules.antivirus.base as base
from mock import MagicMock, patch
from pathlib import Path


class TestClamAV(AbstractTests.TestAntivirus):
    name = "Clam AntiVirus Scanner (Linux)"
    scan_path = Path("/usr/bin/clamdscan")
    scan_args = ('--infected', '--fdpass', '--no-summary', '--stdout')
    module = module.Clam
    scan_clean_stdout = ""
    virusname = "Eicar-Test-Signature"
    scan_virus_stdout = "eicar.com.txt: Eicar-Test-Signature FOUND"
    version = "0.99.4"
    virus_database_version = "24592"
    version_stdout = "ClamAV 0.99.4/24592/Tue May 22 04:34:29 2018"

    @patch.object(module, "get_virus_database_version")
    @patch.object(base.AntivirusUnix, "locate")
    @patch.object(base.AntivirusUnix, "locate_one")
    @patch.object(base.AntivirusUnix, "run_cmd")
    def setUp(self, m_run_cmd, m_locate_one, m_locate,
              m_get_virus_database_version):
        m_run_cmd.return_value = 0, self.version_stdout, ""
        m_locate_one.return_value = self.scan_path
        m_locate.return_value = self.database
        m_get_virus_database_version.return_value = self.virus_database_version
        super().setUp()

    @patch.object(module, "locate_one")
    @patch.object(base.AntivirusUnix, "run_cmd")
    def test_get_virus_db_version(self, m_run_cmd, m_locate_one):
        m_locate_one.return_value = self.scan_path
        m_run_cmd.return_value = 0, self.version_stdout, ""
        version = self.plugin.get_virus_database_version()
        self.assertEquals(version, self.virus_database_version)

    @patch.object(module, "locate_one")
    @patch.object(base.AntivirusUnix, "run_cmd")
    def test_get_virus_db_version_error(self, m_run_cmd, m_locate_one):
        m_locate_one.return_value = self.scan_path
        m_run_cmd.return_value = -1, self.version_stdout, ""
        with self.assertRaises(RuntimeError) as ctx:
            self.plugin.get_virus_database_version()
        self.assertEquals(str(ctx.exception),
                          "Bad return code while getting dbversion")

    @patch.object(module, "locate_one")
    @patch.object(base.AntivirusUnix, "run_cmd")
    def test_get_virus_db_no_version(self, m_run_cmd, m_locate_one):
        m_locate_one.return_value = self.scan_path
        wrong_stdout = "LOREM IPSUM"
        m_run_cmd.return_value = 0, wrong_stdout, ""
        with self.assertRaises(RuntimeError) as ctx:
            self.plugin.get_virus_database_version()
        self.assertEquals(str(ctx.exception),
                          "Cannot read database version in stdout")
