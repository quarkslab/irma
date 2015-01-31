import logging
import unittest

from tests.antivirus.common import GenericEicar
from modules.antivirus.fsecure.fsecure import FSecure


# ============
#  Test Cases
# ============

class FSecureEicar(GenericEicar, unittest.TestCase):

    expected_results = {
        'eicar-passwd.zip': None,
        'eicar.arj': 'EICAR_Test_File [FSE]',
        'eicar.cab': 'EICAR_Test_File [FSE]',
        'eicar.com.pgp': None,
        'eicar.com.txt': 'EICAR_Test_File [FSE]',
        'eicar.lha': 'EICAR_Test_File [FSE]',
        'eicar.lzh': 'EICAR_Test_File [FSE]',
        'eicar.msc': None,
        'eicar.plain': 'EICAR_Test_File [FSE]',
        'eicar.rar': 'EICAR_Test_File [FSE]',
        'eicar.tar': 'EICAR_Test_File [FSE]',
        'eicar.uue': 'EICAR_Test_File [FSE]',
        'eicar.zip': 'EICAR_Test_File [FSE]',
        'eicar_arj.bin': 'EICAR_Test_File [FSE]',
        'eicar_cab.bin': 'EICAR_Test_File [FSE]',
        'eicar_gz.bin': 'EICAR_Test_File [FSE]',
        'eicar_lha.bin': 'EICAR_Test_File [FSE]',
        'eicar_lzh.bin': 'EICAR_Test_File [FSE]',
        'eicar_mime.bin': None,
        'eicar_msc.bin': None,
        'eicar_niveau1.zip': 'EICAR_Test_File [FSE]',
        'eicar_niveau10.zip': 'EICAR_Test_File [FSE]',
        'eicar_niveau11.zip': 'EICAR_Test_File [FSE]',
        'eicar_niveau12.zip': 'EICAR_Test_File [FSE]',
        'eicar_niveau13.zip': None,
        'eicar_niveau14.bin': None,
        'eicar_niveau14.jpg': None,
        'eicar_niveau2.zip': 'EICAR_Test_File [FSE]',
        'eicar_niveau3.zip': 'EICAR_Test_File [FSE]',
        'eicar_niveau30.bin': None,
        'eicar_niveau30.rar': 'EICAR_Test_File [FSE]',
        'eicar_niveau4.zip': 'EICAR_Test_File [FSE]',
        'eicar_niveau5.zip': 'EICAR_Test_File [FSE]',
        'eicar_niveau6.zip': 'EICAR_Test_File [FSE]',
        'eicar_niveau7.zip': 'EICAR_Test_File [FSE]',
        'eicar_niveau8.zip': 'EICAR_Test_File [FSE]',
        'eicar_niveau9.zip': 'EICAR_Test_File [FSE]',
        'eicar_rar.bin': 'EICAR_Test_File [FSE]',
        'eicar_tar.bin': 'EICAR_Test_File [FSE]',
        'eicar_uu.bin': 'EICAR_Test_File [FSE]',
        'eicarhqx_binhex.bin': None,
    }

    antivirus_class = FSecure


if __name__ == '__main__':
    unittest.main()
