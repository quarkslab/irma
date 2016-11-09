import logging
import unittest

from tests.antivirus.common import GenericEicar
from modules.antivirus.virusblokada.virusblokada import VirusBlokAda


# ============
#  Test Cases
# ============

class VirusBlokAdaEicar(GenericEicar, unittest.TestCase):

    expected_results = {
        'eicar-passwd.zip': None,
        'eicar.arj': 'EICAR-Test-File',
        'eicar.cab': 'EICAR-Test-File',
        'eicar.com.pgp': None,
        'eicar.com.txt': 'EICAR-Test-File',
        'eicar.lha': None,
        'eicar.lzh': None,
        'eicar.msc': 'EICAR-Test-File',
        'eicar.plain': 'EICAR-Test-File',
        'eicar.rar': 'EICAR-Test-File',
        'eicar.tar': 'EICAR-Test-File',
        'eicar.uue': 'EICAR-Test-File',
        'eicar.zip': 'EICAR-Test-File',
        'eicar_arj.bin': 'EICAR-Test-File',
        'eicar_cab.bin': 'EICAR-Test-File',
        'eicar_gz.bin': 'EICAR-Test-File',
        'eicar_lha.bin': None,
        'eicar_lzh.bin': None,
        'eicar_mime.bin': 'EICAR-Test-File',
        'eicar_msc.bin': 'EICAR-Test-File',
        'eicar_niveau1.zip': 'EICAR-Test-File',
        'eicar_niveau10.zip': None,
        'eicar_niveau11.zip': None,
        'eicar_niveau12.zip': None,
        'eicar_niveau13.zip': None,
        'eicar_niveau14.bin': None,
        'eicar_niveau14.jpg': None,
        'eicar_niveau2.zip': 'EICAR-Test-File',
        'eicar_niveau3.zip': 'EICAR-Test-File',
        'eicar_niveau30.bin': None,
        'eicar_niveau30.rar': None,
        'eicar_niveau4.zip': 'EICAR-Test-File',
        'eicar_niveau5.zip': 'EICAR-Test-File',
        'eicar_niveau6.zip': 'EICAR-Test-File',
        'eicar_niveau7.zip': 'EICAR-Test-File',
        'eicar_niveau8.zip': None,
        'eicar_niveau9.zip': None,
        'eicar_rar.bin': 'EICAR-Test-File',
        'eicar_tar.bin': 'EICAR-Test-File',
        'eicar_uu.bin': 'EICAR-Test-File',
        'eicarhqx_binhex.bin': 'EICAR-Test-File',
    }

    antivirus_class = VirusBlokAda


if __name__ == '__main__':
    unittest.main()
