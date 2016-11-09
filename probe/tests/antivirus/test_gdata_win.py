import logging
import unittest

from tests.antivirus.common import GenericEicar
from modules.antivirus.gdata_win.gdata_win import GDataWin


# ============
#  Test Cases
# ============

class GDataWinEicar(GenericEicar, unittest.TestCase):

    expected_results = {
        'eicar.cab': 'Virus: EICAR-Test-File (not a virus)',
        'eicar.com.txt': 'Virus: EICAR-Test-File (not a virus) (Engine A)',
        'eicar_niveau2.zip': 'Virus: EICAR-Test-File (not a virus)',
        'eicar_lha.bin': 'Virus: EICAR-Test-File (not a virus)',
        'eicar_gz.bin': 'Virus: EICAR-Test-File (not a virus)',
        'eicarhqx_binhex.bin': 'Virus: Trojan.Script.135850 (Engine A)',
        'eicar_mime.bin': 'Virus: EICAR-Test-File (not a virus)',
        'eicar_cab.bin': 'Virus: EICAR-Test-File (not a virus)',
        'eicar_niveau30.rar': None,
        'eicar_uu.bin': 'Virus: EICAR-Test-File (not a virus)',
        'eicar.plain': 'Virus: EICAR-Test-File (not a virus) (Engine A)',
        'eicar_niveau8.zip': 'Virus: EICAR-Test-File (not a virus)',
        'eicar.lha': 'Virus: EICAR-Test-File (not a virus)',
        'eicar_niveau14.jpg': 'Virus: EICAR-Test-File (not a virus)',
        'eicar_niveau5.zip': 'Virus: EICAR-Test-File (not a virus)',
        'eicar_niveau4.zip': 'Virus: EICAR-Test-File (not a virus)',
        'eicar.zip': 'Virus: EICAR-Test-File (not a virus)',
        'eicar_niveau1.zip': 'Virus: EICAR-Test-File (not a virus)',
        'eicar_niveau30.bin': None,
        'eicar_niveau9.zip': 'Virus: EICAR-Test-File (not a virus)',
        'eicar_niveau7.zip': 'Virus: EICAR-Test-File (not a virus)',
        'eicar.rar': 'Virus: EICAR-Test-File (not a virus)',
        'eicar_niveau11.zip': 'Virus: EICAR-Test-File (not a virus)',
        'eicar_niveau10.zip': 'Virus: EICAR-Test-File (not a virus)',
        'eicar_tar.bin': 'Virus: EICAR-Test-File (not a virus)',
        'eicar_lzh.bin': 'Virus: EICAR-Test-File (not a virus)',
        'eicar_niveau3.zip': 'Virus: EICAR-Test-File (not a virus)',
        'eicar_niveau13.zip': 'Virus: EICAR-Test-File (not a virus)',
        'eicar_niveau14.bin': 'Virus: EICAR-Test-File (not a virus)',
        'eicar.tar': 'Virus: EICAR-Test-File (not a virus)',
        'eicar_niveau6.zip': 'Virus: EICAR-Test-File (not a virus)',
        'eicar_rar.bin': 'Virus: EICAR-Test-File (not a virus)',
        'eicar.uue': 'Virus: EICAR-Test-File (not a virus)',
        'eicar_niveau12.zip': 'Virus: EICAR-Test-File (not a virus)',
        'eicar_arj.bin': 'Virus: EICAR-Test-File (not a virus)',
        'eicar.lzh': 'Virus: EICAR-Test-File (not a virus)',
        'eicar.com.pgp': None,
        'eicar-passwd.zip': None,
        'eicar.arj': 'Virus: EICAR-Test-File (not a virus)',
        'eicar.msc': 'Virus: EICAR-Test-File (not a virus)',
        'eicar_msc.bin': 'Virus: EICAR-Test-File (not a virus)',
    }

    antivirus_class = GDataWin


if __name__ == '__main__':
    unittest.main()
