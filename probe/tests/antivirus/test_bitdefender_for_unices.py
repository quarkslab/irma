import logging
import unittest

from tests.antivirus.common import GenericEicar
from modules.antivirus.bitdefender.bitdefender import BitdefenderForUnices


# ============
#  Test Cases
# ============

class BitdefenderForUnicesEicar(GenericEicar, unittest.TestCase):

    expected_results = {
        'eicar-passwd.zip': None,
        'eicar.arj': 'EICAR-Test-File (not a virus)',
        'eicar.cab': 'EICAR-Test-File (not a virus)',
        'eicar.com.pgp': None,
        'eicar.com.txt': 'EICAR-Test-File (not a virus)',
        'eicar.lha': 'EICAR-Test-File (not a virus)',
        'eicar.lzh': 'EICAR-Test-File (not a virus)',
        'eicar.msc': None,
        'eicar.plain': 'EICAR-Test-File (not a virus)',
        'eicar.rar': 'EICAR-Test-File (not a virus)',
        'eicar.tar': 'EICAR-Test-File (not a virus)',
        'eicar.uue': 'EICAR-Test-File (not a virus)',
        'eicar.zip': 'EICAR-Test-File (not a virus)',
        'eicar_arj.bin': 'EICAR-Test-File (not a virus)',
        'eicar_cab.bin': 'EICAR-Test-File (not a virus)',
        'eicar_gz.bin': 'EICAR-Test-File (not a virus)',
        'eicar_lha.bin': 'EICAR-Test-File (not a virus)',
        'eicar_lzh.bin': 'EICAR-Test-File (not a virus)',
        'eicar_msc.bin': None,
        'eicar_niveau1.zip': 'EICAR-Test-File (not a virus)',
        'eicar_niveau10.zip': 'EICAR-Test-File (not a virus)',
        'eicar_niveau11.zip': 'EICAR-Test-File (not a virus)',
        'eicar_niveau12.zip': 'EICAR-Test-File (not a virus)',
        'eicar_niveau13.zip': 'EICAR-Test-File (not a virus)',
        'eicar_niveau14.bin': None,
        'eicar_niveau14.jpg': None,
        'eicar_niveau2.zip': 'EICAR-Test-File (not a virus)',
        'eicar_niveau3.zip': 'EICAR-Test-File (not a virus)',
        'eicar_niveau30.bin': None,
        'eicar_niveau30.rar': None,
        'eicar_niveau4.zip': 'EICAR-Test-File (not a virus)',
        'eicar_niveau5.zip': 'EICAR-Test-File (not a virus)',
        'eicar_niveau6.zip': 'EICAR-Test-File (not a virus)',
        'eicar_niveau7.zip': 'EICAR-Test-File (not a virus)',
        'eicar_niveau8.zip': 'EICAR-Test-File (not a virus)',
        'eicar_niveau9.zip': 'EICAR-Test-File (not a virus)',
        'eicar_rar.bin': 'EICAR-Test-File (not a virus)',
        'eicar_tar.bin': 'EICAR-Test-File (not a virus)',
        'eicar_uu.bin': 'EICAR-Test-File (not a virus)',
        'eicarhqx_binhex.bin': 'Trojan.Script.135850',
    }

    antivirus_class = BitdefenderForUnices


if __name__ == '__main__':
    unittest.main()
