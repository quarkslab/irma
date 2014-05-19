import logging
import unittest

from tests.antivirus.common import GenericEicar
from modules.antivirus.mcafee_vscl import McAfeeVSCL


# ============
#  Test Cases
# ============

class McAfeeVSCLEicar(GenericEicar, unittest.TestCase):

    expected_results = {
        'eicar.arj': 'EICAR test file',
        'eicar_arj.bin': 'EICAR test file',
        'eicar.cab': 'EICAR test file',
        'eicar_cab.bin': 'EICAR test file',
        'eicar.com.pgp': None,
        'eicar.com.txt': 'EICAR test file',
        'eicar_gz.bin': 'EICAR test file',
        'eicarhqx_binhex.bin': None,
        'eicar.lha': 'EICAR test file',
        'eicar_lha.bin': 'EICAR test file',
        'eicar.lzh': 'EICAR test file',
        'eicar_lzh.bin': 'EICAR test file',
        'eicar.msc': 'EICAR test file',
        'eicar_msc.bin': 'EICAR test file',
        'eicar_niveau10.zip': 'EICAR test file',
        'eicar_niveau11.zip': 'EICAR test file',
        'eicar_niveau12.zip': 'EICAR test file',
        'eicar_niveau13.zip': 'EICAR test file',
        'eicar_niveau14.bin': 'RDN/Generic Flooder',
        'eicar_niveau14.jpg': 'RDN/Generic Flooder',
        'eicar_niveau1.zip': 'EICAR test file',
        'eicar_niveau2.zip': 'EICAR test file',
        'eicar_niveau30.bin': None,
        'eicar_niveau30.rar': None,
        'eicar_niveau3.zip': 'EICAR test file',
        'eicar_niveau4.zip': 'EICAR test file',
        'eicar_niveau5.zip': 'EICAR test file',
        'eicar_niveau6.zip': 'EICAR test file',
        'eicar_niveau7.zip': 'EICAR test file',
        'eicar_niveau8.zip': 'EICAR test file',
        'eicar_niveau9.zip': 'EICAR test file',
        'eicar-passwd.zip': None,
        'eicar.plain': 'EICAR test file',
        'eicar.rar': None,
        'eicar_rar.bin': None,
        'eicar.tar': 'EICAR test file',
        'eicar_tar.bin': 'EICAR test file',
        'eicar_uu.bin': None,
        'eicar.uue': None,
        'eicar.zip': 'EICAR test file',
    }

    antivirus_class = McAfeeVSCL


if __name__ == '__main__':
    unittest.main()
