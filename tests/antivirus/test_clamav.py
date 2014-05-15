import logging
import unittest

from tests.antivirus.common import GenericEicar
from modules.antivirus.clam import Clam


# ============
#  Test Cases
# ============

class ClamAVEicar(GenericEicar, unittest.TestCase):

    expected_results = {
        'eicar.arj': 'Eicar-Test-Signature',
        'eicar_arj.bin': 'Eicar-Test-Signature',
        'eicar.cab': 'Eicar-Test-Signature',
        'eicar_cab.bin': 'Eicar-Test-Signature',
        'eicar.com.pgp': None,
        'eicar.com.txt': 'Eicar-Test-Signature',
        'eicar_gz.bin': 'Eicar-Test-Signature',
        'eicarhqx_binhex.bin': 'Eicar-Test-Signature',
        'eicar.lha': None,
        'eicar_lha.bin': None,
        'eicar.lzh': None,
        'eicar_lzh.bin': None,
        'eicar.msc': None,
        'eicar.msc': 'Eicar-Test-Signature',
        'eicar_msc.bin': 'Eicar-Test-Signature',
        'eicar_niveau10.zip': 'Eicar-Test-Signature',
        'eicar_niveau11.zip': 'Eicar-Test-Signature',
        'eicar_niveau12.zip': 'Eicar-Test-Signature',
        'eicar_niveau13.zip': 'Eicar-Test-Signature',
        'eicar_niveau14.bin': 'Eicar-Test-Signature',
        'eicar_niveau14.jpg': 'Eicar-Test-Signature',
        'eicar_niveau1.zip': 'Eicar-Test-Signature',
        'eicar_niveau2.zip': 'Eicar-Test-Signature',
        'eicar_niveau30.bin': 'Eicar-Test-Signature',
        'eicar_niveau30.rar': 'Eicar-Test-Signature',
        'eicar_niveau3.zip': 'Eicar-Test-Signature',
        'eicar_niveau4.zip': 'Eicar-Test-Signature',
        'eicar_niveau5.zip': 'Eicar-Test-Signature',
        'eicar_niveau6.zip': 'Eicar-Test-Signature',
        'eicar_niveau7.zip': 'Eicar-Test-Signature',
        'eicar_niveau8.zip': 'Eicar-Test-Signature',
        'eicar_niveau9.zip': 'Eicar-Test-Signature',
        'eicar-passwd.zip': None,
        'eicar.plain': 'Eicar-Test-Signature',
        'eicar.rar': None,
        'eicar_rar.bin': None,
        'eicar.tar': 'Eicar-Test-Signature',
        'eicar_tar.bin': 'Eicar-Test-Signature',
        'eicar_uu.bin': None,
        'eicar.uue': None,
        'eicar.zip': 'Eicar-Test-Signature',
    }

    antivirus_class = Clam


if __name__ == '__main__':
    unittest.main()
