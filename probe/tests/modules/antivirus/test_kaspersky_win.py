from .test_antivirus import AbstractTests, set_win_environ
import modules.antivirus.kaspersky_win.kaspersky_win as module
import modules.antivirus.base as base
from mock import patch
from pathlib import Path

set_win_environ()


class TestKasperskyWin(AbstractTests.TestAntivirus):
    name = "Kaspersky Anti-Virus (Windows)"
    scan_path = Path("C:/Program Files (x86)/kaspersky lab/Kaspersky "
                     "Anti-Virus 18.0.0/avp.com")
    scan_args = ('scan', '/i0')
    module = module.KasperskyWin

    scan_clean_stdout = """
AV bases release date: 2018-05-23 12:37:00 (full)
Warning: scan action parameter is ignored due to non-interactive mode is in effect
; --- Settings ---
; Action on detect:     Disinfect automatically
; Scan objects: All objects
; Use iChecker: Yes
; Use iSwift:   Yes
; Try disinfect:        No
; Try delete:   No
; Try delete container: No
; Exclude by mask:      No
; Include by mask:      No
; Objects to scan:
;       "filename"        Enable = Yes    Recursive = No
; ------------------
2018-05-23 19:18:41     Scan_Objects$0137         starting   1%
2018-05-23 19:18:41     Scan_Objects$0137         running    1%
2018-05-23 19:18:41     filename  ok
2018-05-23 19:18:41     Scan_Objects$0137         completed
Info: task 'ods' finished, last error code 0
;  --- Statistics ---
; Time Start:   2018-05-23 19:18:41
; Time Finish:  2018-05-23 19:18:41
; Processed objects:    1
; Total OK:     1
; Total detected:       0
; Suspicions:   0
; Total skipped:        0
; Password protected:   0
; Corrupted:    0
; Errors:       0
;  ------------------

"""  # nopep8
    scan_virus_retcode = 2
    scan_virus_stdout = """
AV bases release date: 2018-05-23 12:37:00 (full)
Warning: scan action parameter is ignored due to non-interactive mode is in effect
; --- Settings ---
; Action on detect:     Disinfect automatically
; Scan objects: All objects
; Use iChecker: Yes
; Use iSwift:   Yes
; Try disinfect:        No
; Try delete:   No
; Try delete container: No
; Exclude by mask:      No
; Include by mask:      No
; Objects to scan:
;       "eicar.com.txt"  Enable = Yes    Recursive = No
; ------------------
2018-05-23 19:19:55     Scan_Objects$0139         starting   1%
2018-05-23 19:19:55     Scan_Objects$0139         running    1%
2018-05-23 19:19:55     eicar.com.txt    detected
EICAR-Test-File
2018-05-23 19:19:59     eicar.com.txt    skipped
2018-05-23 19:19:59     Scan_Objects$0139         completed
Info: task 'ods' finished, last error code 0
;  --- Statistics ---
; Time Start:   2018-05-23 19:19:55
; Time Finish:  2018-05-23 19:19:59
; Processed objects:    1
; Total OK:     0
; Total detected:       1
; Suspicions:   0
; Total skipped:        0
; Password protected:   0
; Corrupted:    0
; Errors:       0
;  ------------------
"""  # nopep8
    virusname = "EICAR-Test-File"
    version = "18.0.0"
    virus_database_version = "2018-05-23 12:37:00 (full)"
    virus_database_version_stdout = """
AV bases release date: 2018-05-23 12:37:00 (full)
Warning: scan action parameter is ignored due to non-interactive mode is in effect
; --- Settings ---
; Action on detect:     Disinfect automatically
; Scan objects: All objects
; Use iChecker: Yes
; Use iSwift:   Yes
; Try disinfect:        No
; Try delete:   No
; Try delete container: No
; Exclude by mask:      No
; Include by mask:      No
; Objects to scan:      No objects
; ------------------
2018-05-23 19:17:49     Scan_Objects$0135         starting   1%
2018-05-23 19:17:49     Scan_Objects$0135         running    100%
2018-05-23 19:17:49     Scan_Objects$0135         completed
Info: task 'ods' finished, last error code 0
;  --- Statistics ---
; Time Start:   2018-05-23 19:17:49
; Time Finish:  2018-05-23 19:17:49
; Processed objects:    0
; Total OK:     0
; Total detected:       0
; Suspicions:   0
; Total skipped:        0
; Password protected:   0
; Corrupted:    0
; Errors:       0
;  ------------------
"""  # nopep8

    @patch.object(module, "get_virus_database_version")
    @patch.object(module, "get_version")
    @patch.object(base.AntivirusWindows, "locate")
    @patch.object(base.AntivirusWindows, "locate_one")
    @patch.object(base.AntivirusWindows, "run_cmd")
    def setUp(self, m_run_cmd, m_locate_one, m_locate,
              m_get_version, m_get_virus_database_version):
        m_run_cmd.return_value = 0, "", ""
        m_locate_one.return_value = self.scan_path
        m_locate.return_value = self.database
        m_get_version.return_value = self.version
        m_get_virus_database_version.return_value = self.virus_database_version
        super().setUp()

    @patch.object(module, "run_cmd")
    def test_get_virus_db_version(self, m_run_cmd):
        m_run_cmd.return_value = 0, self.virus_database_version_stdout, ""
        version = self.plugin.get_virus_database_version()
        self.assertEquals(version, self.virus_database_version)

    @patch.object(module, "locate_one")
    def test_get_version(self, m_locate_one):
        m_locate_one().read_text.return_value = \
            self.version_stdout
        version = self.plugin.get_version()
        self.assertEquals(version, self.version)

    def test_get_version_error(self):
        self.plugin.scan_path = Path("Wrong scan path")
        with self.assertRaises(RuntimeError):
            self.plugin.get_version()
