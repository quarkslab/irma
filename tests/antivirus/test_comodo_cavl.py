import logging
import unittest

from tests.antivirus.common import GenericEicar
from modules.antivirus.comodo.cavl import ComodoCAVL


# ============
#  Test Cases
# ============

class ComodoCAVLEicar(GenericEicar, unittest.TestCase):

    expected_results = {
        'eicar-passwd.zip': None,
        'eicar.arj': 'ApplicUnwnt',
        'eicar.cab': 'ApplicUnwnt',
        'eicar.com.pgp': None,
        'eicar.com.txt': 'ApplicUnwnt',
        'eicar.lha': 'ApplicUnwnt',
        'eicar.lzh': 'ApplicUnwnt',
        'eicar.msc': None,
        'eicar.plain': 'Malware',
        'eicar.rar': 'ApplicUnwnt',
        'eicar.tar': None,
        'eicar.uue': None,
        'eicar.zip': 'ApplicUnwnt',
        'eicar_arj.bin': 'ApplicUnwnt',
        'eicar_cab.bin': 'ApplicUnwnt',
        'eicar_gz.bin': 'ApplicUnwnt',
        'eicar_lha.bin': 'ApplicUnwnt',
        'eicar_lzh.bin': 'ApplicUnwnt',
        'eicar_mime.bin': 'ApplicUnwnt',
        'eicar_msc.bin': None,
        'eicar_niveau1.zip': 'ApplicUnwnt',
        'eicar_niveau10.zip': None,
        'eicar_niveau11.zip': None,
        'eicar_niveau12.zip': None,
        'eicar_niveau13.zip': None,
        'eicar_niveau14.bin': None,
        'eicar_niveau14.jpg': None,
        'eicar_niveau2.zip': 'ApplicUnwnt',
        'eicar_niveau3.zip': 'ApplicUnwnt',
        'eicar_niveau30.bin': None,
        'eicar_niveau30.rar': None,
        'eicar_niveau4.zip': 'ApplicUnwnt',
        'eicar_niveau5.zip': None,
        'eicar_niveau6.zip': None,
        'eicar_niveau7.zip': None,
        'eicar_niveau8.zip': None,
        'eicar_niveau9.zip': None,
        'eicar_rar.bin': 'ApplicUnwnt',
        'eicar_tar.bin': None,
        'eicar_uu.bin': None,
        'eicarhqx_binhex.bin': None,
    }

    antivirus_class = ComodoCAVL


if __name__ == '__main__':
    unittest.main()
