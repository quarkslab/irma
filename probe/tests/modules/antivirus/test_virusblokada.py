from .test_antivirus import AbstractTests
import modules.antivirus.virusblokada.virusblokada as module
import modules.antivirus.base as base
from mock import patch
from pathlib import Path


class TestVirusBlokada(AbstractTests.TestAntivirus):
    name = "VirusBlokAda Console Scanner (Linux)"
    scan_path = Path("/usr/bin/vbacl")
    scan_args = ('-AF+', '-RW+', '-HA=3', '-VM+', '-AR+', '-ML+',
                 '-CH+', '-SFX+',)
    module = module.VirusBlokAda

    scan_clean_stdout = """
+----------------------------------------------------+
|           VirusBlokAda (Console scanner)           |
| Vba32 Linux 3.12.32.0 / 2018.05.21 09:08 (Vba32.L) |
|        Copyright (c) 1993-2018 by VBA Ltd.         |
+----------------------------------------------------+
Key file not found
Demo mode
Program settings:
-QU -AF -AR -CH -ML -RW -SFX -VM -HA=3 -J=1


filename

Directories       : 0      Files in archives:        Files on disks:
Archives:                  - total      : 0          - total      : 1
- scanned         : 0      - scanned    : 0          - scanned    : 1
- contain viruses : 0      - infected   : 0          - infected   : 0
- deleted         : 0      - suspicious : 0          - suspicious : 0
                                                     - cured      : 0
Mail messages:             Attached files            - deleted    : 0
- scanned         : 0      - total      : 0          - renamed    : 0
- contain viruses : 0      - scanned    : 0          - quarantined: 0
- suspicious      : 0      - infected   : 0
- deleted         : 0      - suspicious : 0
                           - cured      : 0
                           - deleted    : 0

Startup    : 15:50:36 22-05-2018
End        : 15:50:36 22-05-2018
Total time : 00:00:00
"""  # nopep8
    scan_virus_retcode = 6
    scan_virus_stdout = """
+----------------------------------------------------+
|           VirusBlokAda (Console scanner)           |
| Vba32 Linux 3.12.32.0 / 2018.05.21 09:08 (Vba32.L) |
|        Copyright (c) 1993-2018 by VBA Ltd.         |
+----------------------------------------------------+
Key file not found
Demo mode
Program settings:
-QU -AF -AR -CH -ML -RW -SFX -VM -HA=3 -J=1


eicar.com.txt
eicar.com.txt : infected EICAR-Test-File

Directories       : 0      Files in archives:        Files on disks:
Archives:                  - total      : 0          - total      : 1
- scanned         : 0      - scanned    : 0          - scanned    : 1
- contain viruses : 0      - infected   : 0          - infected   : 1
- deleted         : 0      - suspicious : 0          - suspicious : 0
                                                     - cured      : 0
Mail messages:             Attached files            - deleted    : 0
- scanned         : 0      - total      : 0          - renamed    : 0
- contain viruses : 0      - scanned    : 0          - quarantined: 0
- suspicious      : 0      - infected   : 0
- deleted         : 0      - suspicious : 0
                           - cured      : 0
                           - deleted    : 0

Startup    : 15:51:37 22-05-2018
End        : 15:51:37 22-05-2018
Total time : 00:00:00"""  # nopep8
    virusname = "EICAR-Test-File"
    version = "3.12.32.0"
    version_stdout = """
+----------------------------------------------------+
|           VirusBlokAda (Console scanner)           |
| Vba32 Linux 3.12.32.0 / 2018.05.21 09:08 (Vba32.L) |
|        Copyright (c) 1993-2018 by VBA Ltd.         |
+----------------------------------------------------+
Key file not found
Demo mode
Start from the command line:
 vba32l  [path] ... [path]  [-switch] ... [-switch],
               @filename - scan files from filelist
       switch - specifies program options:

-?[+|-]        - show help screen;
-H[+|-]        - show help screen;
-HELP[+|-]     - show help screen;
-AF[+|-]       - all files;
-SL[+|-]       - follow symbolic links;
-RW[+|-]       - detect Spyware, Adware, Riskware;
-CH[+|-]       - switch on cache while scanning objects;
-FC[+|-]       - cure infected files;
-FD[+|-]       - delete infected files;
-FR[+|-]       - rename infected files;                                                                                 
-FM+[directory]- move infected files to selected directory (by default /var/virus);
-SD[+|-]       - delete suspicious files;
-SR[+|-]       - rename suspicious files;
-SM+[directory]- move suspicious files to selected directory (by default /var/virus);
-HA=[0|1|2|3]  - heuristic analysis level (0 - disabled, 2 - maximum);
-QI[+[directory]|-] - copy infected object to Quarantine;
-QS[+[directory]|-] - copy suspicious object to Quarantine;
-R=[filename]  - save report to file (VBA32.RPT by default);
-R+[filename]  - append report to file (VBA32.RPT by default);
-SYSLOG[+|-]   - send scanning events to syslog;
-L=[filename]  - save list of infected files to file (VBA32.LST);
-L+[filename]  - append list of infected files to file (VBA32.LST);
-QU[+|-]       - allow the program to be interrupted (by default);
-DB=directory  - search virus definitions update in
                 selected directory on startup;
-OK[+|-]       - include "clean" filenames in report;
-TRUSTZONE[+|-] - distinguish "trusted" files (use with -OK);
-AR[+|-]       - enable archives scanning;
-AL=[file_size,kB] - don't scan archives larger than the specified value;
-AD[+|-]       - delete archives containing infected files;
-SFX[+|-]      - detect installers of malware;
-ML[+|-]       - mail scanning;
-MD[+|-]       - delete messages containing infected files;
-VL[+|-]       - view list of viruses known to program;
-VM[+|-]       - show macros information in documents;
-SI[+|-]       - additional information about program support;
-LNG=suffix    - select language file VBA32<suffix>.LNG;
-KF={directory|path} - specify path to key file;
-EXT=          - specify list of file extensions to be checked;
-EXT+          - add user defined file extensions to default list;
-EXT-          - remove file extensions from default list;
-WK[+|-]       - wait for any key when finished;
-SP[+|-]       - show overall check progress;
-J[+|-|=thread_count] - multithreaded mode, count of simultaneously
                 processed files can be set to default value (-J, -J+,
                 preferred) or explicitely (-J=count);
  The following switches are active by default: -QU -RW

Program settings:
-HELP -QU -AF -RW -HA=1 -J=1
"""  # nopep8
    virus_database_version = "2018.05.21 09:08"
    virus_database_version_stdout = version_stdout

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
    def test_get_virus_db(self, m_run_cmd, m_locate_one):
        m_locate_one.return_value = self.scan_path
        m_run_cmd.return_value = 0, self.virus_database_version_stdout, ""
        version = self.plugin.get_virus_database_version()
        self.assertEquals(version, self.virus_database_version)
