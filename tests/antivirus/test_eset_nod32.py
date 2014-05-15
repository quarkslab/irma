import logging
import unittest

from tests.antivirus.common import GenericEicar
from modules.antivirus.eset_nod32 import EsetNod32


# ============
#  Test Cases
# ============

class EsetNod32Eicar(GenericEicar, unittest.TestCase):

    expected_results = {
        'eicar.arj': 'Eicar test file',
        'eicar_arj.bin': 'Eicar test file',
        'eicar.cab': 'Eicar test file',
        'eicar_cab.bin': 'Eicar test file',
        'eicar.com.pgp': None,
        'eicar.com.txt': 'Eicar test file',
        'eicar_gz.bin': 'Eicar test file',
        'eicarhqx_binhex.bin': None,
        'eicar.lha': 'Eicar test file',
        'eicar_lha.bin': 'Eicar test file',
        'eicar.lzh': 'Eicar test file',
        'eicar_lzh.bin': 'Eicar test file',
        'eicar_mime.bin': 'Eicar test file',
        'eicar.msc': None,
        'eicar_msc.bin': None,
        'eicar_niveau10.zip': None,
        'eicar_niveau11.zip': None,
        'eicar_niveau12.zip': None,
        'eicar_niveau13.zip': 'Archbomb.ZIP trojan',
        'eicar_niveau14.bin': 'Archbomb.ZIP trojan',
        'eicar_niveau14.jpg': 'Archbomb.ZIP trojan',
        'eicar_niveau1.zip': 'Eicar test file',
        'eicar_niveau2.zip': 'Eicar test file',
        'eicar_niveau30.bin': 'Archbomb.RAR trojan',
        'eicar_niveau30.rar': 'Archbomb.RAR trojan',
        'eicar_niveau3.zip': 'Eicar test file',
        'eicar_niveau4.zip': 'Eicar test file',
        'eicar_niveau5.zip': 'Eicar test file',
        'eicar_niveau6.zip': 'Eicar test file',
        'eicar_niveau7.zip': 'Eicar test file',
        'eicar_niveau8.zip': 'Eicar test file',
        'eicar_niveau9.zip': 'Eicar test file',
        'eicar-passwd.zip': None,
        'eicar.plain': 'Eicar test file',
        'eicar.rar': 'Eicar test file',
        'eicar_rar.bin': 'Eicar test file',
        'eicar.tar': 'Eicar test file',
        'eicar_tar.bin': 'Eicar test file',
        'eicar_uu.bin': None,
        'eicar.uue': None,
        'eicar.zip': 'Eicar test file',
    }

    antivirus_class = EsetNod32


if __name__ == '__main__':
    unittest.main()
