from .test_antivirus import AbstractTests, base
import modules.antivirus.avast.avast as module
from mock import patch, MagicMock
from pathlib import Path


class TestAvast(AbstractTests.TestAntivirus):
    name = "Avast Core Security (Linux)"
    scan_path = Path("/usr/bin/scan")
    scan_args = ('-b', '-f', '-u')
    scan_virus_stdout = "eicar.com.txt\tVirusName"
    version = "1.2.3.4"
    version_stdout = "mocked version 1.2.3.4"
    path = "/a/random/path"
    module = module.AvastCoreSecurity
    scan_clean_stdout = ""
    scan_result = None
    database = ["/a/first/virusdb", "/a/second/virusdb"]

    @patch("modules.antivirus.avast.avast.Path")
    @patch.object(base.AntivirusUnix, "run_cmd")
    @patch.object(base.AntivirusUnix, "locate")
    @patch.object(base.AntivirusUnix, "locate_one")
    def setUp(self, m_locate_one, m_locate, m_run_cmd, m_Path):
        m_run_cmd.return_value = 0, self.version_stdout, ""
        m_locate_one.return_value = self.scan_path
        m_locate.return_value = self.database
        m_Path().__truediv__().read_text.return_value = self.database
        super().setUp()
