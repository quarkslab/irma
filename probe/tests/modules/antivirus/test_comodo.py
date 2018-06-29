from .test_antivirus import AbstractTests
import modules.antivirus.comodo.cavl as module
import modules.antivirus.base as base
from mock import MagicMock, patch
from pathlib import Path


class TestComodo(AbstractTests.TestAntivirus):
    name = "Comodo Antivirus (Linux)"
    scan_path = Path("/opt/COMODO/cmdscan")
    scan_args = ("-v", "-s")
    module = module.ComodoCAVL

    scan_result = ""
    scan_clean_stdout = """
-----== Scan Start ==-----
filename ---> Not Virus
-----== Scan End ==-----
Number of Scanned Files: 1
Number of Found Viruses: 0
"""

    scan_virus_retcode = 0
    scan_virus_stdout = """
-----== Scan Start ==-----
eicar.com.txt ---> Found Virus, Malware Name is VirusName
-----== Scan End ==-----
Number of Scanned Files: 1
Number of Found Viruses: 1
"""
    version = "1.1.268025.1"
    virus_database_version = "2018-05-22"
    version_stdout = "1.1.268025.1"

    @patch("modules.antivirus.comodo.cavl.Path")
    @patch.object(base.AntivirusUnix, "locate")
    @patch.object(base.AntivirusUnix, "run_cmd")
    def setUp(self, m_run_cmd, m_locate, m_Path):
        m_Path(self.scan_path).return_value = self.scan_path
        m_locate.return_value = self.database
        self.scan_path = m_Path(self.scan_path)
        m_Path().read_text.return_value = self.version_stdout
        m_stat = MagicMock()
        m_stat.st_mtime = float("1526975640.7491271")
        m_Path().stat.return_value = m_stat
        super().setUp()
