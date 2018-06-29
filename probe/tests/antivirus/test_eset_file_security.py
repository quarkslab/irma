import logging
import unittest

from tests.antivirus.common import GenericEicar
from modules.antivirus.eset.eset_file_security import EsetFileSecurity


# ============
#  Test Cases
# ============

class EsetFileSecurityEicar(GenericEicar, unittest.TestCase):

    expected_results = {
        'eicar-passwd.zip': None,
        'eicar.arj': 'Eicar test file',
        'eicar.cab': 'Eicar test file',
        'eicar.com.pgp': None,
        'eicar.com.txt': 'Eicar test file',
        'eicar.lha': 'Eicar test file',
        'eicar.lzh': 'Eicar test file',
        'eicar.msc': None,
        'eicar.plain': 'Eicar test file',
        'eicar.rar': 'Eicar test file',
        'eicar.tar': 'Eicar test file',
        'eicar.uue': None,
        'eicar.zip': 'Eicar test file',
        'eicar_arj.bin': 'Eicar test file',
        'eicar_cab.bin': 'Eicar test file',
        'eicar_gz.bin': 'Eicar test file',
        'eicar_lha.bin': 'Eicar test file',
        'eicar_lzh.bin': 'Eicar test file',
        'eicar_mime.bin': 'Eicar test file',
        'eicar_msc.bin': None,
        'eicar_niveau1.zip': 'Eicar test file',
        'eicar_niveau10.zip': None,
        'eicar_niveau11.zip': None,
        'eicar_niveau12.zip': None,
        'eicar_niveau13.zip': 'Archbomb.ZIP trojan',
        'eicar_niveau14.bin': 'Archbomb.ZIP trojan',
        'eicar_niveau14.jpg': 'Archbomb.ZIP trojan',
        'eicar_niveau2.zip': 'Eicar test file',
        'eicar_niveau3.zip': 'Eicar test file',
        'eicar_niveau30.bin': 'Archbomb.RAR trojan',
        'eicar_niveau30.rar': 'Archbomb.RAR trojan',
        'eicar_niveau4.zip': 'Eicar test file',
        'eicar_niveau5.zip': 'Eicar test file',
        'eicar_niveau6.zip': 'Eicar test file',
        'eicar_niveau7.zip': 'Eicar test file',
        'eicar_niveau8.zip': 'Eicar test file',
        'eicar_niveau9.zip': 'Eicar test file',
        'eicar_rar.bin': 'Eicar test file',
        'eicar_tar.bin': 'Eicar test file',
        'eicar_uu.bin': None,
        'eicarhqx_binhex.bin': None,
    }

    antivirus_class = EsetFileSecurity


if __name__ == '__main__':
    unittest.main()
