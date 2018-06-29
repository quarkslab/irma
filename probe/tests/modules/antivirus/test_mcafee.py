from .test_antivirus import AbstractTests
import modules.antivirus.mcafee.vscl as module
import modules.antivirus.base as base
from mock import patch
from pathlib import Path


class TestMcAfee(AbstractTests.TestAntivirus):
    name = "McAfee VirusScan Command Line scanner (Linux)"
    scan_path = Path("/usr/local/uvscan/uvscan")
    scan_args = ('--ASCII', '--ANALYZE', '--MANALYZE', '--MACRO-HEURISTICS',
                 '--RECURSIVE', '--UNZIP',)
    module = module.McAfeeVSCL

    scan_clean_stdout = """
McAfee VirusScan Command Line for Linux64 Version: 6.0.4.564
Copyright (C) 2013 McAfee, Inc.
(408) 988-3832 EVALUATION COPY - May 23 2018

AV Engine version: 5600.1067 for Linux64.
Dat set version: 8901 created May 22 2018
Scanning for 668700 viruses, trojans and variants.



Time: 00:00.00


Thank you for choosing to evaluate VirusScan Command Line from McAfee.
This  version of the software is for Evaluation Purposes Only and may be
used  for  up to 30 days to determine if it meets your requirements.  To
license  the  software,  or to  obtain  assistance during the evaluation
process,  please call (408) 988-3832.  If you  choose not to license the
software,  you  need  to remove it from your system.  All  use  of  this
software is conditioned upon compliance with the license terms set forth
in the README.TXT file.
"""  # nopep8
    scan_virus_stdout = """
McAfee VirusScan Command Line for Linux64 Version: 6.0.4.564
Copyright (C) 2013 McAfee, Inc.
(408) 988-3832 EVALUATION COPY - May 23 2018

AV Engine version: 5600.1067 for Linux64.
Dat set version: 8901 created May 22 2018
Scanning for 668700 viruses, trojans and variants.

eicar.com.txt ... Found: EICAR test file NOT a virus.


Time: 00:00.00


Thank you for choosing to evaluate VirusScan Command Line from McAfee.
This  version of the software is for Evaluation Purposes Only and may be
used  for  up to 30 days to determine if it meets your requirements.  To
license  the  software,  or to  obtain  assistance during the evaluation
process,  please call (408) 988-3832.  If you  choose not to license the
software,  you  need  to remove it from your system.  All  use  of  this
software is conditioned upon compliance with the license terms set forth
in the README.TXT file.
"""  # nopep8
    virusname = "EICAR test file"
    version = "5600.1067"
    version_stdout = """
Copyright (C) 2013 McAfee, Inc.
(408) 988-3832 EVALUATION COPY - May 23 2018

AV Engine version: 5600.1067 for Linux64.
Dat set version: 8901 created May 22 2018
Scanning for 668700 viruses, trojans and variants.
"""  # nopep8
    virus_database_version = "8901"
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
