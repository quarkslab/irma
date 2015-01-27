import logging
import unittest

from tests.antivirus.common import GenericEicar
from modules.antivirus.escan.escan import Escan


# ============
#  Test Cases
# ============

class BitdefenderForUnicesEicar(GenericEicar, unittest.TestCase):

    expected_results = {
        'eicar-passwd.zip': None,
        'eicar.arj': 'EICAR-Test-File (not a virus)(DB)',
        'eicar.cab': 'EICAR-Test-File (not a virus)(DB)',
        'eicar.com.pgp': None,
        'eicar.com.txt': 'EICAR-Test-File (not a virus)(DB)',
        'eicar.lha': 'EICAR-Test-File (not a virus)(DB)',
        'eicar.lzh': 'EICAR-Test-File (not a virus)(DB)',
        'eicar.msc': 'EICAR-Test-File (not a virus)(DB)',
        'eicar.plain': 'EICAR-Test-File (not a virus)(DB)',
        'eicar.rar': 'EICAR-Test-File (not a virus)(DB)',
        'eicar.tar': 'EICAR-Test-File (not a virus)(DB)',
        'eicar.uue': 'EICAR-Test-File (not a virus)(DB)',
        'eicar.zip': 'EICAR-Test-File (not a virus)(DB)',
        'eicar_arj.bin': 'EICAR-Test-File (not a virus)(DB)',
        'eicar_cab.bin': 'EICAR-Test-File (not a virus)(DB)',
        'eicar_gz.bin': 'EICAR-Test-File (not a virus)(DB)',
        'eicar_lha.bin': 'EICAR-Test-File (not a virus)(DB)',
        'eicar_lzh.bin': 'EICAR-Test-File (not a virus)(DB)',
        'eicar_msc.bin': 'EICAR-Test-File (not a virus)(DB)',
        'eicar_niveau1.zip': 'EICAR-Test-File (not a virus)(DB)',
        'eicar_niveau10.zip': 'EICAR-Test-File (not a virus)(DB)',
        'eicar_niveau11.zip': 'EICAR-Test-File (not a virus)(DB)',
        'eicar_niveau12.zip': 'EICAR-Test-File (not a virus)(DB)',
        'eicar_niveau13.zip': 'EICAR-Test-File (not a virus)(DB)',
        'eicar_niveau14.bin': 'EICAR-Test-File (not a virus)(DB)',
        'eicar_niveau14.jpg': 'EICAR-Test-File (not a virus)(DB)',
        'eicar_niveau2.zip': 'EICAR-Test-File (not a virus)(DB)',
        'eicar_niveau3.zip': 'EICAR-Test-File (not a virus)(DB)',
        'eicar_niveau30.bin': None,
        'eicar_niveau30.rar': None,
        'eicar_niveau4.zip': 'EICAR-Test-File (not a virus)(DB)',
        'eicar_niveau5.zip': 'EICAR-Test-File (not a virus)(DB)',
        'eicar_niveau6.zip': 'EICAR-Test-File (not a virus)(DB)',
        'eicar_niveau7.zip': 'EICAR-Test-File (not a virus)(DB)',
        'eicar_niveau8.zip': 'EICAR-Test-File (not a virus)(DB)',
        'eicar_niveau9.zip': 'EICAR-Test-File (not a virus)(DB)',
        'eicar_rar.bin': 'EICAR-Test-File (not a virus)(DB)',
        'eicar_tar.bin': 'EICAR-Test-File (not a virus)(DB)',
        'eicar_uu.bin': 'EICAR-Test-File (not a virus)(DB)',
        'eicarhqx_binhex.bin': 'Trojan.Script.135850(DB)',
    }

    antivirus_class = Escan


if __name__ == '__main__':
    unittest.main()
