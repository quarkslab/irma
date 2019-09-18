from .test_antivirus import AbstractTests, set_win_environ
import modules.antivirus.symantec_win.symantec_win as module
import modules.antivirus.base as base
from mock import patch
from pathlib import Path

set_win_environ()


class TestSymantecWin(AbstractTests.TestAntivirus):
    name = "Symantec Anti-Virus (Windows)"
    scan_path = Path("C:/Program Files (x86)/Symantec/Symantec "
                     "Endpoint Protection/14.2.760.0000.105/Bin/DoScan.exe")
    scan_args = ('/ScanFile',)
    module = module.SymantecWin
    database = []
    scan_virus_stdout = """
30060A0C1904,2,2,1,VAGRANT-AUNRN59,vagrant,,,,,,,16777216,"Scan Complete:  Risks: 0   Scanned: 0   Files/Folders/Drives Omitted: 0 Trusted Files Skipped: 0",1531219462,,0,0:0:0:0:0,,,,0,,,,,,,,,,,{A715442A-7069-4892-8CC3-D37F89FD31E5},,,,WORKGROUP,52:54:00:B3:00:6F,14.2.760.0,,,,,,,,,,,,,,,,0,,,,,,,,,,,,,,,,,,,,0,9D01A172578A48689D88916107ED57CE,0,30060A0C1904,,,3,Default,0,,,,0,,0,,0
30060A0C1B25,5,1,2,VAGRANT-AUNRN59,vagrant,EICAR Test String,eicar.com.txt,5,1,14,256,37769284,"",1531219457,,0,201	4	6	1	525	0	0	0	0	0	0,0,11101,0,1,0,0,0,0,,0,0,4,0,,{A715442A-7069-4892-8CC3-D37F89FD31E5},,,,WORKGROUP,52:54:00:B3:00:6F,14.2.760.0,,,,,,,,,,,,,,,,0,,406e1d22-43e6-4ad6-9d14-462c89a8afe2,0,,502		68	2	275A021BBFB6489E54D471899F7DB9D1663FC695EC2FE2A2C4538AABF651FD0F		0	0		0	0	0		0	0,,1,,0,0,0,0,0,,,0,0,0,,,,0,30060A0C1B25,0,,0,Default,0,,,,0,,0,,0
30060A0C1B25,46,1,2,VAGRANT-AUNRN59,vagrant,EICAR Test String,eicar.com.txt,5,1,19,256,33556484,"",1531219463,,0,101	{DA28F878-8E1C-4827-A8D3-5B9430C909F8}	0	1				EICAR Test String	1;0	0	0	406e1d22-43e6-4ad6-9d14-462c89a8afe2	0,0,11101,0,0,0,,,0,,0,0,1,0,,{A715442A-7069-4892-8CC3-D37F89FD31E5},,,,WORKGROUP,52:54:00:B3:00:6F,14.2.760.0,,,,,,,,,,,,,,,,999,,5f7fb208-740a-4bb0-a6c5-21d4f189649e,0,,502		68	2	275A021BBFB6489E54D471899F7DB9D1663FC695EC2FE2A2C4538AABF651FD0F		127	127		127	0	0	eicar.com.txt	1	0,,1,,1,127,0,0,0,,,1,127,0,,,,0,30060A0C1B25,0,,0,Default,0,,,,73014444032,,0,,0
30060A0C1B25,5,1,2,VAGRANT-AUNRN59,vagrant,,eicar.com.txt,5,1,19,256,37750852,"",1531219463,,0,,1610389545,11101,0,0,0,,,0,,0,0,4,0,,{A715442A-7069-4892-8CC3-D37F89FD31E5},,,,WORKGROUP,52:54:00:B3:00:6F,14.2.760.0,,,,,,,,,,,,,,,,0,,5f7fb208-740a-4bb0-a6c5-21d4f189649e,515375104,,,,1,,0,0,0,0,0,,,0,0,0,,,,0,30060A0C1B25,0,,0,Default,0,,,,0,,0,,0
30060A0C1B25,51,1,2,VAGRANT-AUNRN59,vagrant,EICAR Test String,eicar.com.txt,5,1,19,256,37750852,"",1531219463,,0,101	{DA28F878-8E1C-4827-A8D3-5B9430C909F8}	0	1				EICAR Test String	1;0	0	0	406e1d22-43e6-4ad6-9d14-462c89a8afe2	0,515375104,11101,0,0,0,,,0,,0,0,1,0,,{A715442A-7069-4892-8CC3-D37F89FD31E5},,,,WORKGROUP,52:54:00:B3:00:6F,14.2.760.0,,,,,,,,,,,,,,,,999,,5f7fb208-740a-4bb0-a6c5-21d4f189649e,515375104,,502		68	2	275A021BBFB6489E54D471899F7DB9D1663FC695EC2FE2A2C4538AABF651FD0F		127	127		127	0	0	eicar.com.txt	1	0,,1,,1,127,0,0,0,,,1,127,0,,,,0,30060A0C1B25,0,,0,Default,0,,,,73014444032,,0,,0
30060A0C1B25,95,1,2,VAGRANT-AUNRN59,vagrant,EICAR Test String,eicar.com.txt,11,4,19,256,37750852,"",1531219463,,0,101	{DA28F878-8E1C-4827-A8D3-5B9430C909F8}	0	1				EICAR Test String	1;0	0	0	406e1d22-43e6-4ad6-9d14-462c89a8afe2	0,515375104,11101,0,0,0,0,0,0,,0,0,1,0,,{A715442A-7069-4892-8CC3-D37F89FD31E5},,,,,,,,,,,,,,,,,,,,,,999,,5f7fb208-740a-4bb0-a6c5-21d4f189649e,515375104,,502		68	2	275A021BBFB6489E54D471899F7DB9D1663FC695EC2FE2A2C4538AABF651FD0F		127	127		127	0	0	eicar.com.txt	1	0,,1,,1,127,0,0,0,,,1,127,0,,,,0,30060A0C1B34,0,,0,,0,,,,73014444032,,0,,0
30060A0C1C06,3,2,1,VAGRANT-AUNRN59,vagrant,,,,,,,16777216,"Scan started on selected drives and folders and all extensions.",1531219464,,0,,,,,0,,,,,,,,,,,{A715442A-7069-4892-8CC3-D37F89FD31E5},,,,WORKGROUP,52:54:00:B3:00:6F,14.2.760.0,,,,,,,,,,,,,,,,0,,,,,,,,,,,,,,,,,,,,0,F8D32BE75C924ED7BD7276DAE9DE1915,0,30060A0C1C06,,,3,Default,0,,,,0,,0,,0
30060A0C1C06,46,1,1,VAGRANT-AUNRN59,vagrant,EICAR Test String,eicar.com.txt,5,1,5,256,33554436,"",1531219464,,0,101	{DC7A622E-2111-427D-9244-CF705D6880E5}	0	2				EICAR Test String	1;0	0	0		0,0,11101,0,0,0,,,0,,0,0,4,0,,{A715442A-7069-4892-8CC3-D37F89FD31E5},,,,WORKGROUP,52:54:00:B3:00:6F,14.2.760.0,,,,,,,,,,,,,,,,999,,42cf3da3-a343-40a7-9ede-fd856ffc9d21,0,,502		68	2	275A021BBFB6489E54D471899F7DB9D1663FC695EC2FE2A2C4538AABF651FD0F		127	127		127	0	0	eicar.com.txt	1	0,,1,,1,1,119,71,166,,,1,127,0,,,F8D32BE75C924ED7BD7276DAE9DE1915,0,30060A0C1C06,0,,0,Default,0,,,,73014444032,,0,,0
"""  # nopep8
    # Scanning a clean file wont produce any new lines in log file
    scan_clean_stdout = ""
    virusname = "EICAR Test String"
    version = "14.2.760.0000.105"
    virus_database_version = "unavailable"

    @patch.object(module, "get_version")
    @patch.object(base.AntivirusWindows, "locate")
    @patch.object(base.AntivirusWindows, "locate_one")
    @patch.object(base.AntivirusWindows, "run_cmd")
    def setUp(self, m_run_cmd, m_locate_one, m_locate,
              m_get_version):
        m_run_cmd.return_value = 0, "", ""
        m_locate_one.return_value = self.scan_path
        m_locate.return_value = self.database
        m_get_version.return_value = self.version
        super().setUp()

    @patch.object(module, "locate_one")
    def test_get_version(self, m_locate_one):
        m_locate_one.return_value = \
            self.scan_path
        version = self.plugin.get_version()
        self.assertEquals(version, self.version)

    def test_get_version_error(self):
        self.plugin.scan_path = Path("Wrong scan path")
        with self.assertRaises(RuntimeError):
            self.plugin.get_version()

    def test_scan_clean(self):
        # running scan just append to log file
        pass

    def test_scan_virus(self):
        # running scan just append to log file
        pass
