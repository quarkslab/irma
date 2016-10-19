import logging
import unittest

from tests.antivirus.common import GenericEicar
from modules.antivirus.kaspersky_win.kaspersky_win import KasperskyWin


# ============
#  Test Cases
# ============

class KasperskyWinEicar(GenericEicar, unittest.TestCase):

    expected_results = {
        'eicar-passwd.zip': None,
        'eicar.arj': 'EICAR-Test-File',
        'eicar.cab': 'EICAR-Test-File',
        'eicar.com.pgp': None,
        'eicar.com.txt': 'EICAR-Test-File',
        'eicar.lha': 'EICAR-Test-File',
        'eicar.lzh': 'EICAR-Test-File',
        'eicar.msc': 'EICAR-Test-File',
        'eicar.plain': 'EICAR-Test-File',
        'eicar.rar': 'EICAR-Test-File',
        'eicar.tar': 'EICAR-Test-File',
        'eicar.uue': 'EICAR-Test-File',
        'eicar.zip': 'EICAR-Test-File',
        'eicar_arj.bin': 'EICAR-Test-File',
        'eicar_cab.bin': 'EICAR-Test-File',
        'eicar_gz.bin': 'EICAR-Test-File',
        'eicar_lha.bin': 'EICAR-Test-File',
        'eicar_lzh.bin': 'EICAR-Test-File',
        'eicar_mime.bin': 'EICAR-Test-File',
        'eicar_msc.bin': 'EICAR-Test-File',
        'eicar_niveau1.zip': 'EICAR-Test-File',
        'eicar_niveau10.zip': 'EICAR-Test-File',
        'eicar_niveau11.zip': 'EICAR-Test-File',
        'eicar_niveau12.zip': 'EICAR-Test-File',
        'eicar_niveau13.zip': 'EICAR-Test-File',
        'eicar_niveau14.bin': 'EICAR-Test-File',
        'eicar_niveau14.jpg': 'EICAR-Test-File',
        'eicar_niveau2.zip': 'EICAR-Test-File',
        'eicar_niveau3.zip': 'EICAR-Test-File',
        'eicar_niveau30.bin': 'EICAR-Test-File',
        'eicar_niveau30.rar': 'EICAR-Test-File',
        'eicar_niveau4.zip': 'EICAR-Test-File',
        'eicar_niveau5.zip': 'EICAR-Test-File',
        'eicar_niveau6.zip': 'EICAR-Test-File',
        'eicar_niveau7.zip': 'EICAR-Test-File',
        'eicar_niveau8.zip': 'EICAR-Test-File',
        'eicar_niveau9.zip': 'EICAR-Test-File',
        'eicar_rar.bin': 'EICAR-Test-File',
        'eicar_tar.bin': 'EICAR-Test-File',
        'eicar_uu.bin': 'EICAR-Test-File',
        'eicarhqx_binhex.bin': 'EICAR-Test-File',
    }

    antivirus_class = KasperskyWin


if __name__ == '__main__':
    unittest.main()
