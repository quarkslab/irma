from .test_antivirus import AbstractTests
import modules.antivirus.drweb.drweb as module
import modules.antivirus.base as base
from mock import patch
from pathlib import Path


class TestDrWeb(AbstractTests.TestAntivirus):
    name = "DrWeb Antivirus (Linux)"
    scan_path = Path("/usr/bin/drweb-ctl")
    scan_args = ('scan',)
    module = module.DrWeb

    scan_clean_stdout = """
/tmp/filename - Ok
Scanned objects: 1, scan errors: 0, threats found: 0, threats neutralized: 0.
Scanned 0.66 KB in 12.29 s with speed 0.05 KB/s.
"""

    scan_virus_retcode = 0
    scan_virus_stdout = """
eicar.com.txt - infected with EICAR Test File (NOT a Virus!)
Scanned objects: 1, scan errors: 0, threats found: 1, threats neutralized: 0.
Scanned 0.07 KB in 0.10 s with speed 0.68 KB/s.
"""
    virusname = "EICAR Test File (NOT a Virus!)"
    version = "11.0.7.1804031813"
    version_stdout = "drweb-ctl 11.0.7.1804031813"

    @patch.object(base.AntivirusUnix, "locate")
    @patch.object(base.AntivirusUnix, "locate_one")
    @patch.object(base.AntivirusUnix, "run_cmd")
    def setUp(self, m_run_cmd, m_locate_one, m_locate):
        m_run_cmd.return_value = 0, self.version_stdout, ""
        m_locate_one.return_value = self.scan_path
        m_locate.return_value = self.database
        super().setUp()
