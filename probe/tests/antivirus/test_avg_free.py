import logging
import unittest

from tests.antivirus.common import GenericEicar
from modules.antivirus.avg.avg import AVGAntiVirusFree


# ============
#  Test Cases
# ============

class AVGAntiVirusFreeEicar(GenericEicar, unittest.TestCase):

    expected_results = {
        'eicar_arj.bin': 'EICAR_Test',
        'eicar.arj': 'EICAR_Test',
        'eicar_cab.bin': 'EICAR_Test',
        'eicar.cab': 'EICAR_Test',
        'eicar.com.pgp': None,
        'eicar.com.txt': 'EICAR_Test',
        'eicar_gz.bin': 'EICAR_Test',
        'eicarhqx_binhex.bin': 'EICAR_Test',
        'eicar_lha.bin': 'EICAR_Test',
        'eicar.lha': 'EICAR_Test',
        'eicar_lzh.bin': 'EICAR_Test',
        'eicar.lzh': 'EICAR_Test',
        'eicar_mime.bin': 'EICAR_Test',
        'eicar_msc.bin': 'EICAR_Test',
        'eicar.msc': 'EICAR_Test',
        'eicar_niveau10.zip': 'EICAR_Test',
        'eicar_niveau11.zip': 'EICAR_Test',
        'eicar_niveau12.zip': 'EICAR_Test',
        'eicar_niveau13.zip': 'EICAR_Test',
        'eicar_niveau14.bin': 'EICAR_Test',
        'eicar_niveau14.jpg': 'EICAR_Test',
        'eicar_niveau1.zip': 'EICAR_Test',
        'eicar_niveau2.zip': 'EICAR_Test',
        'eicar_niveau30.bin': 'EICAR_Test',
        'eicar_niveau30.rar': 'EICAR_Test',
        'eicar_niveau3.zip': 'EICAR_Test',
        'eicar_niveau4.zip': 'EICAR_Test',
        'eicar_niveau5.zip': 'EICAR_Test',
        'eicar_niveau6.zip': 'EICAR_Test',
        'eicar_niveau7.zip': 'EICAR_Test',
        'eicar_niveau8.zip': 'EICAR_Test',
        'eicar_niveau9.zip': 'EICAR_Test',
        'eicar-passwd.zip': None,
        'eicar.plain': 'EICAR_Test',
        'eicar_rar.bin': 'EICAR_Test',
        'eicar.rar': 'EICAR_Test',
        'eicar_tar.bin': 'EICAR_Test',
        'eicar.tar': 'EICAR_Test',
        'eicar_uu.bin': None,
        'eicar.uue': ('EICAR_Test', None),
        'eicar.zip': 'EICAR_Test',
    }

    antivirus_class = AVGAntiVirusFree


if __name__ == '__main__':
    unittest.main()
