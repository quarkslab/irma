import logging
import unittest

from tests.antivirus.common import GenericEicar
from modules.antivirus.comodo_cavl import ComodoCAVL


# ============
#  Test Cases
# ============

class ComodoCAVLEicar(GenericEicar, unittest.TestCase):

    expected_results = {
        'eicar-passwd.zip': None,
        'eicar.arj': None,
        'eicar.cab': None,
        'eicar.com.pgp': None,
        'eicar.com.txt': None,
        'eicar.lha': None,
        'eicar.lzh': None,
        'eicar.msc': None,
        'eicar.plain': None,
        'eicar.rar': None,
        'eicar.tar': None,
        'eicar.uue': None,
        'eicar.zip': None,
        'eicar_arj.bin': None,
        'eicar_cab.bin': None,
        'eicar_gz.bin': None,
        'eicar_lha.bin': None,
        'eicar_lzh.bin': None,
        'eicar_mime.bin': None,
        'eicar_msc.bin': None,
        'eicar_niveau1.zip': None,
        'eicar_niveau10.zip': None,
        'eicar_niveau11.zip': None,
        'eicar_niveau12.zip': None,
        'eicar_niveau13.zip': None,
        'eicar_niveau14.bin': None,
        'eicar_niveau14.jpg': None,
        'eicar_niveau2.zip': None,
        'eicar_niveau3.zip': None,
        'eicar_niveau30.bin': None,
        'eicar_niveau30.rar': None,
        'eicar_niveau4.zip': None,
        'eicar_niveau5.zip': None,
        'eicar_niveau6.zip': None,
        'eicar_niveau7.zip': None,
        'eicar_niveau8.zip': None,
        'eicar_niveau9.zip': None,
        'eicar_rar.bin': None,
        'eicar_tar.bin': None,
        'eicar_uu.bin': None,
        'eicarhqx_binhex.bin': None,
    }

    antivirus_class = ComodoCAVL


if __name__ == '__main__':
    unittest.main()
