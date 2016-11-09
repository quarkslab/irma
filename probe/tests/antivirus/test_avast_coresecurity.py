import logging
import unittest

from tests.antivirus.common import GenericEicar
from modules.antivirus.avast.avast import AvastCoreSecurity


# ============
#  Test Cases
# ============

class AvastCoreSecurityEicar(GenericEicar, unittest.TestCase):

    expected_results = {
        'eicar-passwd.zip': None,
        'eicar.arj': 'EICAR Test-NOT virus!!!',
        'eicar.cab': 'EICAR Test-NOT virus!!!',
        'eicar.com.pgp': None,
        'eicar.com.txt': 'EICAR Test-NOT virus!!!',
        'eicar.lha': 'EICAR Test-NOT virus!!!',
        'eicar.lzh': 'EICAR Test-NOT virus!!!',
        'eicar.msc': 'EICAR Test-NOT virus!!!',
        'eicar.plain': 'EICAR Test-NOT virus!!!',
        'eicar.rar': 'EICAR Test-NOT virus!!!',
        'eicar.tar': 'EICAR Test-NOT virus!!!',
        'eicar.uue': 'EICAR Test-NOT virus!!!',
        'eicar.zip': 'EICAR Test-NOT virus!!!',
        'eicar_arj.bin': 'EICAR Test-NOT virus!!!',
        'eicar_cab.bin': 'EICAR Test-NOT virus!!!',
        'eicar_gz.bin': 'EICAR Test-NOT virus!!!',
        'eicar_lha.bin': 'EICAR Test-NOT virus!!!',
        'eicar_lzh.bin': 'EICAR Test-NOT virus!!!',
        'eicar_msc.bin': 'EICAR Test-NOT virus!!!',
        'eicar_niveau1.zip': 'EICAR Test-NOT virus!!!',
        'eicar_niveau10.zip': None,
        'eicar_niveau11.zip': None,
        'eicar_niveau12.zip': None,
        'eicar_niveau13.zip': None,
        'eicar_niveau14.bin': None,
        'eicar_niveau14.jpg': None,
        'eicar_niveau2.zip': 'EICAR Test-NOT virus!!!',
        'eicar_niveau3.zip': 'EICAR Test-NOT virus!!!',
        'eicar_niveau30.bin': None,
        'eicar_niveau30.rar': None,
        'eicar_niveau4.zip': 'EICAR Test-NOT virus!!!',
        'eicar_niveau5.zip': 'EICAR Test-NOT virus!!!',
        'eicar_niveau6.zip': 'EICAR Test-NOT virus!!!',
        'eicar_niveau7.zip': 'EICAR Test-NOT virus!!!',
        'eicar_niveau8.zip': 'EICAR Test-NOT virus!!!',
        'eicar_niveau9.zip': 'EICAR Test-NOT virus!!!',
        'eicar_rar.bin': 'EICAR Test-NOT virus!!!',
        'eicar_tar.bin': 'EICAR Test-NOT virus!!!',
        'eicar_uu.bin': 'EICAR Test-NOT virus!!!',
        'eicarhqx_binhex.bin': None,
    }

    antivirus_class = AvastCoreSecurity


if __name__ == '__main__':
    unittest.main()
