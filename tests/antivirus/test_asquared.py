import logging
import unittest

from tests.antivirus.common import GenericEicar
from modules.antivirus.emsisoft.asquared import ASquaredCmd


# ============
#  Test Cases
# ============

class ASquaredCmdEicar(GenericEicar, unittest.TestCase):

    expected_results = {
        'eicar.cab': 'EICAR-Test-File (not a virus) (B)',
        'eicar.com.txt': 'EICAR-Test-File (not a virus) (B)',
        'eicar_niveau2.zip': 'EICAR-Test-File (not a virus) (B)',
        'eicar_lha.bin': 'EICAR-Test-File (not a virus) (B)',
        'eicar_gz.bin': 'EICAR-Test-File (not a virus) (B)',
        'eicarhqx_binhex.bin': 'Trojan.Script.135850 (B)',
        'eicar_mime.bin': 'EICAR-Test-File (not a virus) (B)',
        'eicar_cab.bin': 'EICAR-Test-File (not a virus) (B)',
        'eicar_niveau30.rar': None,
        'eicar_uu.bin': 'EICAR-Test-File (not a virus) (B)',
        'eicar.plain': 'EICAR-Test-File (not a virus) (B)',
        'eicar_niveau8.zip': 'EICAR-Test-File (not a virus) (B)',
        'eicar.lha': 'EICAR-Test-File (not a virus) (B)',
        'eicar_niveau14.jpg': 'EICAR-Test-File (not a virus) (B)',
        'eicar_niveau5.zip': 'EICAR-Test-File (not a virus) (B)',
        'eicar_niveau4.zip': 'EICAR-Test-File (not a virus) (B)',
        'eicar.zip': 'EICAR-Test-File (not a virus) (B)',
        'eicar_niveau1.zip': 'EICAR-Test-File (not a virus) (B)',
        'eicar_niveau30.bin': None,
        'eicar_niveau9.zip': 'EICAR-Test-File (not a virus) (B)',
        'eicar_niveau7.zip': 'EICAR-Test-File (not a virus) (B)',
        'eicar.rar': 'EICAR-Test-File (not a virus) (B)',
        'eicar_niveau11.zip': 'EICAR-Test-File (not a virus) (B)',
        'eicar_niveau10.zip': 'EICAR-Test-File (not a virus) (B)',
        'eicar_tar.bin': 'EICAR-Test-File (not a virus) (B)',
        'eicar_lzh.bin': 'EICAR-Test-File (not a virus) (B)',
        'eicar_niveau3.zip': 'EICAR-Test-File (not a virus) (B)',
        'eicar_niveau13.zip': 'EICAR-Test-File (not a virus) (B)',
        'eicar_niveau14.bin': 'EICAR-Test-File (not a virus) (B)',
        'eicar.tar': 'EICAR-Test-File (not a virus) (B)',
        'eicar_niveau6.zip': 'EICAR-Test-File (not a virus) (B)',
        'eicar_rar.bin': 'EICAR-Test-File (not a virus) (B)',
        'eicar.uue': 'EICAR-Test-File (not a virus) (B)',
        'eicar_niveau12.zip': 'EICAR-Test-File (not a virus) (B)',
        'eicar_arj.bin': 'EICAR-Test-File (not a virus) (B)',
        'eicar.lzh': 'EICAR-Test-File (not a virus) (B)',
        'eicar.com.pgp': None,
        'eicar-passwd.zip': None,
        'eicar.arj': 'EICAR-Test-File (not a virus) (B)',
        'eicar.msc': 'EICAR-Test-File (not a virus) (B)',
        'eicar_msc.bin': 'EICAR-Test-File (not a virus) (B)',
    }

    antivirus_class = ASquaredCmd


if __name__ == '__main__':
    unittest.main()
