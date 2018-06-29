from .test_antivirus import AbstractTests
import modules.antivirus.escan.escan as module
import modules.antivirus.base as base
from mock import patch
from pathlib import Path


class TestEscan(AbstractTests.TestAntivirus):
    name = "eScan Antivirus (Linux)"
    scan_path = Path("/usr/bin/escan")
    scan_args = ('--log-only', '--recursion', '--pack', '--archives',
                 '--heuristic', '--scan-ext', '--display-none',
                 '--display-infected',)
    module = module.Escan

    scan_clean_stdout = """Failed to apply scan priority, default priority will be applied
This product is running on trial, please activate your license key.
*******************************************************
	  eScan Anti-Virus for Linux  
Copyright (C), Microworld Technologies Inc.
	 Website: http://www.escanav.com
*******************************************************

-------------------------------------------------------
		Scan Configuration
-------------------------------------------------------
Scan Memory on Execution	: Yes
Scan Packed			: Yes
Scan Archives			: Yes
Scan Mails			: Yes
Use Heuristics Scanning		: Yes
Recursive			: Yes
Follow Symbolic Links		: No
Cross File System		: No
Scan Action			: Log only
Scan extensions			: --display-none
Log Level			: Infected

Initializing AV... Done
Memory Scan Started  Done
Scan Started. Please wait
--------------------Scan Statistics--------------------
Scanned directories		0
Scanned objects			1
Infected objects		0
Suspicious objects		0
Disinfected objects		0
Uncurable objects		0
Viruses found			0
Deleted objects			0
Rename objects			0
Quarantined objects		0
Corrupt objects			0
Encrypted objects		0
Scan errors			1
Actions failed			0
-------------------------------------------------------"""  # nopep8
    scan_virus_retcode = 0
    scan_virus_stdout = """Failed to apply scan priority, default priority will be applied
This product is running on trial, please activate your license key.
*******************************************************
	  eScan Anti-Virus for Linux  
Copyright (C), Microworld Technologies Inc.
	 Website: http://www.escanav.com
*******************************************************

-------------------------------------------------------
		Scan Configuration
-------------------------------------------------------
Scan Memory on Execution	: Yes
Scan Packed			: Yes
Scan Archives			: Yes
Scan Mails			: Yes
Use Heuristics Scanning		: Yes
Recursive			: Yes
Follow Symbolic Links		: No
Cross File System		: No
Scan Action			: Log only
Scan extensions			: --display-none
Log Level			: Infected

Initializing AV... Done
Memory Scan Started  Done
Scan Started. Please wait
eicar.com.txt [INFECTED][EICAR-Test-File (not a virus)(DB)]
--------------------Scan Statistics--------------------
Scanned directories		0
Scanned objects			1
Infected objects		1
Suspicious objects		0
Disinfected objects		0
Uncurable objects		0
Viruses found			1
Deleted objects			0
Rename objects			0
Quarantined objects		0
Corrupt objects			0
Encrypted objects		0
Scan errors			0
Actions failed			0
-------------------------------------------------------
"""  # nopep8
    virusname = "EICAR-Test-File (not a virus)(DB)"
    version = "7.0.21"
    version_stdout = """
Failed to apply scan priority, default priority will be applied
This product is running on trial, please activate your license key.
*******************************************************
	  eScan Anti-Virus for Linux  
Copyright (C), Microworld Technologies Inc.
	 Website: http://www.escanav.com
*******************************************************


Error Getting License Info
MicroWorld eScan For Linux Version : 7.0.21
MicroWorld Admin Version		  : 5.5-1.Debian.6.0.3MicroWorld Anti-virus Version		  : 5.5-1.Debian.6.0.3"""  # nopep8

    virus_database_version = "7.76075 (22/05/2018)"
    virus_database_version_stdout = """
Failed to apply scan priority, default priority will be applied
This product is running on trial, please activate your license key.
*******************************************************
	  eScan Anti-Virus for Linux  
Copyright (C), Microworld Technologies Inc.
	 Website: http://www.escanav.com
*******************************************************

Anti-virus Engine & Virus Info

+---------------------------------------------+
| Anti-virus Engine Version :  7.76075        |
| Date of Virus Signature   :  22/05/2018     |
| Virus Count               :  11993780       |
+---------------------------------------------+"""  # nopep8

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
    def test_get_virus_db_error(self, m_run_cmd, m_locate_one):
        m_locate_one.return_value = self.scan_path
        m_run_cmd.return_value = -1, self.version_stdout, ""
        with self.assertRaises(RuntimeError):
            self.plugin.get_virus_database_version()

    @patch.object(module, "locate_one")
    @patch.object(base.AntivirusUnix, "run_cmd")
    def test_get_virus_db_no_version(self, m_run_cmd, m_locate_one):
        m_locate_one.return_value = self.scan_path
        wrong_stdout = "LOREM IPSUM"
        m_run_cmd.return_value = 0, wrong_stdout, ""
        with self.assertRaises(RuntimeError):
            self.plugin.get_virus_database_version()

    @patch.object(module, "locate_one")
    @patch.object(base.AntivirusUnix, "run_cmd")
    def test_get_virus_db_version(self, m_run_cmd, m_locate_one):
        m_locate_one.return_value = self.scan_path
        m_run_cmd.return_value = 0, self.virus_database_version_stdout, ""
        version = self.plugin.get_virus_database_version()
        self.assertEquals(version, self.virus_database_version)

    @patch.object(module, "locate_one")
    @patch.object(base.AntivirusUnix, "run_cmd")
    def test_get_virus_db_no_release(self, m_run_cmd, m_locate_one):
        m_locate_one.return_value = self.scan_path
        wrong_stdout = "| Anti-virus Engine Version :  7.76075        |"
        m_run_cmd.return_value = 0, wrong_stdout, ""
        version = self.plugin.get_virus_database_version()
        self.assertEquals(version, "7.76075")
