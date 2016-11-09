import logging
import unittest

from tests.antivirus.common import GenericEicar
from modules.antivirus.avira_win.avira_win import AviraWin


# ============
#  Test Cases
# ============

class AviraWinEicar(GenericEicar, unittest.TestCase):

    expected_results = {
        'eicar.cab': 'Eicar-Test-Signature',
        'eicar.com.txt': 'Eicar-Test-Signature',
        'eicar_niveau2.zip': 'Eicar-Test-Signature',
        'eicar_lha.bin': 'Eicar-Test-Signature',
        'eicar_gz.bin': 'Eicar-Test-Signature',
        'eicarhqx_binhex.bin': 'Eicar-Test-Signature',
        'eicar_mime.bin': 'Eicar-Test-Signature',
        'eicar_cab.bin': 'Eicar-Test-Signature',
        'eicar_niveau30.rar': None,
        'eicar_uu.bin': 'Eicar-Test-Signature',
        'eicar.plain': 'Eicar-Test-Signature',
        'eicar_niveau8.zip': 'Eicar-Test-Signature',
        'eicar.lha': 'Eicar-Test-Signature',
        'eicar_niveau14.jpg': None,
        'eicar_niveau5.zip': 'Eicar-Test-Signature',
        'eicar_niveau4.zip': 'Eicar-Test-Signature',
        'eicar.zip': 'Eicar-Test-Signature',
        'eicar_niveau1.zip': 'Eicar-Test-Signature',
        'eicar_niveau30.bin': None,
        'eicar_niveau9.zip': 'Eicar-Test-Signature',
        'eicar_niveau7.zip': 'Eicar-Test-Signature',
        'eicar.rar': 'Eicar-Test-Signature',
        'eicar_niveau11.zip': None,
        'eicar_niveau10.zip': None,
        'eicar_tar.bin': 'Eicar-Test-Signature',
        'eicar_lzh.bin': 'Eicar-Test-Signature',
        'eicar_niveau3.zip': 'Eicar-Test-Signature',
        'eicar_niveau13.zip': None,
        'eicar_niveau14.bin': None,
        'eicar.tar': 'Eicar-Test-Signature',
        'eicar_niveau6.zip': 'Eicar-Test-Signature',
        'eicar_rar.bin': 'Eicar-Test-Signature',
        'eicar-passwd.zip': None,
        'eicar_niveau12.zip': None,
        'eicar_arj.bin': 'Eicar-Test-Signature',
        'eicar.lzh': 'Eicar-Test-Signature',
        'eicar.com.pgp': None,
        'eicar.uue': 'Eicar-Test-Signature',
        'eicar.arj': 'Eicar-Test-Signature',
        'eicar.msc': 'Eicar-Test-Signature',
        'eicar_msc.bin': 'Eicar-Test-Signature',
    }

    antivirus_class = AviraWin


if __name__ == '__main__':
    unittest.main()
