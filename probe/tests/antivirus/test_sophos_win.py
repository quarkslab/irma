import logging
import unittest

from tests.antivirus.common import GenericEicar
from modules.antivirus.sophos_win.sophos_win import SophosWin


# ============
#  Test Cases
# ============

class SophosWinEicar(GenericEicar, unittest.TestCase):

    expected_results = {
        'eicar-passwd.zip': None,
        'eicar.arj': 'EICAR-AV-Test',
        'eicar.cab': 'EICAR-AV-Test',
        'eicar.com.pgp': None,
        'eicar.com.txt': 'EICAR-AV-Test',
        'eicar.lha': 'EICAR-AV-Test',
        'eicar.lzh': 'EICAR-AV-Test',
        'eicar.msc': None,
        'eicar.plain': 'EICAR-AV-Test',
        'eicar.rar': 'EICAR-AV-Test',
        'eicar.tar': 'EICAR-AV-Test',
        'eicar.uue': 'EICAR-AV-Test',
        'eicar.zip': 'EICAR-AV-Test',
        'eicar_arj.bin': 'EICAR-AV-Test',
        'eicar_cab.bin': 'EICAR-AV-Test',
        'eicar_gz.bin': 'EICAR-AV-Test',
        'eicar_lha.bin': 'EICAR-AV-Test',
        'eicar_lzh.bin': 'EICAR-AV-Test',
        'eicar_mime.bin': 'EICAR-AV-Test',
        'eicar_msc.bin': None,
        'eicar_niveau1.zip': 'EICAR-AV-Test',
        'eicar_niveau10.zip': None,
        'eicar_niveau11.zip': None,
        'eicar_niveau12.zip': None,
        'eicar_niveau13.zip': None,
        'eicar_niveau14.bin': None,
        'eicar_niveau14.jpg': None,
        'eicar_niveau2.zip': 'EICAR-AV-Test',
        'eicar_niveau3.zip': 'EICAR-AV-Test',
        'eicar_niveau30.bin': None,
        'eicar_niveau30.rar': None,
        'eicar_niveau4.zip': 'EICAR-AV-Test',
        'eicar_niveau5.zip': None,
        'eicar_niveau6.zip': None,
        'eicar_niveau7.zip': None,
        'eicar_niveau8.zip': None,
        'eicar_niveau9.zip': None,
        'eicar_rar.bin': 'EICAR-AV-Test',
        'eicar_tar.bin': 'EICAR-AV-Test',
        'eicar_uu.bin': 'EICAR-AV-Test',
        'eicarhqx_binhex.bin': None,
    }

    antivirus_class = SophosWin


if __name__ == '__main__':
    unittest.main()
