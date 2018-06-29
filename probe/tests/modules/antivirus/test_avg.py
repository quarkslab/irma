from .test_antivirus import AbstractTests
import modules.antivirus.avg.avg as module
import modules.antivirus.base as base
from mock import patch
from pathlib import Path


class TestAvg(AbstractTests.TestAntivirus):
    name = "AVG AntiVirus Free (Linux)"
    scan_path = Path("/usr/bin/avgscan")
    scan_args = ('--heur', '--paranoid', '--arc', '--macrow', '--pwdw',
                 '--pup')
    module = module.AVGAntiVirusFree

    scan_clean_stdout = """AVG command line Anti-Virus scanner
Copyright (c) 2013 AVG Technologies CZ

Virus database version: 4793/15678
Virus database release date: Mon, 21 May 2018 13:00:00 +0000


Files scanned     :  1(1)
Infections found  :  0(0)
PUPs found        :  0
Files healed      :  0
Warnings reported :  0
Errors reported   :  0
    """

    scan_virus_retcode = 4
    virusname = "EICAR_Test"
    scan_virus_stdout = """AVG command line Anti-Virus scanner
Copyright (c) 2013 AVG Technologies CZ

Virus database version: 4793/15678
Virus database release date: Mon, 21 May 2018 13:00:00 +0000

eicar.com.txt  Virus identified EICAR_Test

Files scanned     :  1(1)
Infections found  :  1(1)
PUPs found        :  0
Files healed      :  0
Warnings reported :  0
Errors reported   :  0
    """
    version = "13.0.3118"
    virus_database_version = "4793/15678 (21 May 2018)"
    version_stdout = """AVG command line controller
Copyright (c) 2013 AVG Technologies CZ


------ AVG status ------
AVG version	:  13.0.3118
Components version :  Aspam:3111, Cfg:3109, Cli:3115, Common:3110, Core:4793, Doc:3115, Ems:3111, Initd:3113, Lng:3112, Oad:3118, Other:3109, Scan:3115, Sched:3110, Update:3109

Last update        :  Tue, 22 May 2018 07:52:31 +0000

------ License status ------
License number     :  LUOTY-674PL-VRWOV-APYEG-ZXHMA-E
License version    :  10
License type       :  FREE
License expires on :  
Registered user    :  
Registered company :  

------ WD status ------
Component	State		Restarts	UpTime
Avid		running		0		13 minute(s)
Oad		running		0		13 minute(s)
Sched		running		0		13 minute(s)
Tcpd		running		0		13 minute(s)
Update		stopped		0		-


------ Sched status ------
Task name          Next runtime                      Last runtime
Virus update       Tue, 22 May 2018 18:04:00 +0000   Tue, 22 May 2018 07:46:29 +0000
Program update     -                                 -                              
User counting      Wed, 23 May 2018 07:46:29 +0000   Tue, 22 May 2018 07:46:29 +0000



------ Tcpd status ------
E-mails checked   :  0
SPAM messages     :  0
Phishing messages :  0
E-mails infected  :  0
E-mails dropped   :  0


------ Avid status ------
Virus database reload times     :  0
Virus database version          :  4793/15678
Virus database release date     :  Mon, 21 May 2018 13:00:00 +0000
Virus database shared in memory :  yes


------ Oad status ------
Files scanned     :  0(0)
Infections found  :  0(0)
PUPs found        :  0
Files healed      :  0
Warnings reported :  0
Errors reported   :  0

Operation successful.
"""  # nopep8

    @patch.object(base.AntivirusUnix, "locate")
    @patch.object(base.AntivirusUnix, "locate_one")
    @patch.object(base.AntivirusUnix, "run_cmd")
    def setUp(self, m_run_cmd, m_locate_one, m_locate):
        m_run_cmd.return_value = 0, self.version_stdout, ""
        m_locate_one.return_value = self.scan_path
        m_locate.return_value = self.database
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
    def test_get_virus_db_no_release(self, m_run_cmd, m_locate_one):
        m_locate_one.return_value = self.scan_path
        wrong_stdout = "Virus database version          :  4793/15678"
        m_run_cmd.return_value = 0, wrong_stdout, ""
        version = self.plugin.get_virus_database_version()
        self.assertEquals(version, "4793/15678")
