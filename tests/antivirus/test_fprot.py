import logging
import unittest

from tests.antivirus.common import GenericEicar
from modules.antivirus.fprot import FProt


# ============
#  Test Cases
# ============

class FProtEicar(GenericEicar, unittest.TestCase):

    expected_results = {
        'eicar.arj': 'EICAR_Test_File (exact, not disinfectable)',
        'eicar_arj.bin': 'EICAR_Test_File (exact, not disinfectable)',
        'eicar.cab': 'EICAR_Test_File (exact, not disinfectable)',
        'eicar_cab.bin': 'EICAR_Test_File (exact, not disinfectable)',
        'eicar.com.pgp': None,
        'eicar.com.txt': 'EICAR_Test_File (exact)',
        'eicar_gz.bin': 'EICAR_Test_File (exact, not disinfectable)',
        'eicarhqx_binhex.bin': None,
        'eicar.lha': 'EICAR_Test_File (exact, not disinfectable)',
        'eicar_lha.bin': 'EICAR_Test_File (exact, not disinfectable)',
        'eicar.lzh': 'EICAR_Test_File (exact, not disinfectable)',
        'eicar_lzh.bin': 'EICAR_Test_File (exact, not disinfectable)',
        'eicar_mime.bin': 'EICAR_Test_File (exact, not disinfectable)',
        'eicar.msc': 'EICAR_Test_File (exact, not disinfectable)',
        'eicar_msc.bin': 'EICAR_Test_File (exact, not disinfectable)',
        'eicar_niveau10.zip': None,
        'eicar_niveau11.zip': None,
        'eicar_niveau12.zip': None,
        'eicar_niveau13.zip': None,
        'eicar_niveau14.bin': None,
        'eicar_niveau14.jpg': None,
        'eicar_niveau1.zip': 'EICAR_Test_File (exact, not disinfectable)',
        'eicar_niveau2.zip': 'EICAR_Test_File (exact, not disinfectable)',
        'eicar_niveau30.bin': None,
        'eicar_niveau30.rar': None,
        'eicar_niveau3.zip': 'EICAR_Test_File (exact, not disinfectable)',
        'eicar_niveau4.zip': 'EICAR_Test_File (exact, not disinfectable)',
        'eicar_niveau5.zip': None,
        'eicar_niveau6.zip': None,
        'eicar_niveau7.zip': None,
        'eicar_niveau8.zip': None,
        'eicar_niveau9.zip': None,
        'eicar-passwd.zip': None,
        'eicar.plain': 'EICAR_Test_File (exact)',
        'eicar.rar': 'EICAR_Test_File (exact, not disinfectable)',
        'eicar_rar.bin': 'EICAR_Test_File (exact, not disinfectable)',
        'eicar.tar': 'EICAR_Test_File (exact, not disinfectable)',
        'eicar_tar.bin': 'EICAR_Test_File (exact, not disinfectable)',
        'eicar_uu.bin': 'EICAR_Test_File (exact, not disinfectable)',
        'eicar.uue': 'EICAR_Test_File (exact, not disinfectable)',
        'eicar.zip': 'EICAR_Test_File (exact, not disinfectable)',
    }

    antivirus_class = FProt


if __name__ == '__main__':
    unittest.main()
