import logging
import unittest

from tests.antivirus.common import GenericEicar
from modules.antivirus.drweb.drweb import DrWeb


# ============
#  Test Cases
# ============

class ZonerEicar(GenericEicar, unittest.TestCase):

    expected_results = {
        'eicar-passwd.zip': None,
        'eicar.arj': 'EICAR Test File (NOT a Virus!)',
        'eicar.cab': 'EICAR Test File (NOT a Virus!)',
        'eicar.com.pgp': None,
        'eicar.com.txt': 'EICAR Test File (NOT a Virus!)',
        'eicar.lha': 'EICAR Test File (NOT a Virus!)',
        'eicar.lzh': 'EICAR Test File (NOT a Virus!)',
        'eicar.msc': 'EICAR Test File (NOT a Virus!)',
        'eicar.plain': 'EICAR Test File (NOT a Virus!)',
        'eicar.rar': 'EICAR Test File (NOT a Virus!)',
        'eicar.tar': 'EICAR Test File (NOT a Virus!)',
        'eicar.uue': 'EICAR Test File (NOT a Virus!)',
        'eicar.zip': 'EICAR Test File (NOT a Virus!)',
        'eicar_arj.bin': 'EICAR Test File (NOT a Virus!)',
        'eicar_cab.bin': 'EICAR Test File (NOT a Virus!)',
        'eicar_gz.bin': 'EICAR Test File (NOT a Virus!)',
        'eicar_lha.bin': 'EICAR Test File (NOT a Virus!)',
        'eicar_lzh.bin': 'EICAR Test File (NOT a Virus!)',
        'eicar_mime.bin': 'EICAR Test File (NOT a Virus!)',
        'eicar_msc.bin': 'EICAR Test File (NOT a Virus!)',
        'eicar_niveau1.zip': 'EICAR Test File (NOT a Virus!)',
        'eicar_niveau10.zip': None,
        'eicar_niveau11.zip': None,
        'eicar_niveau12.zip': None,
        'eicar_niveau13.zip': None,
        'eicar_niveau14.bin': None,
        'eicar_niveau14.jpg': None,
        'eicar_niveau2.zip': 'EICAR Test File (NOT a Virus!)',
        'eicar_niveau3.zip': 'EICAR Test File (NOT a Virus!)',
        'eicar_niveau30.bin': None,
        'eicar_niveau30.rar': None,
        'eicar_niveau4.zip': 'EICAR Test File (NOT a Virus!)',
        'eicar_niveau5.zip': 'EICAR Test File (NOT a Virus!)',
        'eicar_niveau6.zip': 'EICAR Test File (NOT a Virus!)',
        'eicar_niveau7.zip': 'EICAR Test File (NOT a Virus!)',
        'eicar_niveau8.zip': None,
        'eicar_niveau9.zip': None,
        'eicar_rar.bin': 'EICAR Test File (NOT a Virus!)',
        'eicar_tar.bin': 'EICAR Test File (NOT a Virus!)',
        'eicar_uu.bin': 'EICAR Test File (NOT a Virus!)',
        'eicarhqx_binhex.bin': None,
    }

    antivirus_class = DrWeb


if __name__ == '__main__':
    unittest.main()
