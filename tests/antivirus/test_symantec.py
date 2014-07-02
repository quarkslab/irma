import logging
import unittest

from tests.antivirus.common import GenericEicar
from modules.antivirus.symantec.symantec import Symantec


# ============
#  Test Cases
# ============

class SymantecEicar(GenericEicar, unittest.TestCase):

    expected_results = {
        'eicar-passwd.zip': None,
        'eicar.arj': 'EICAR Test String',
        'eicar.cab': 'EICAR Test String',
        'eicar.com.pgp': None,
        'eicar.com.txt': 'EICAR Test String',
        'eicar.lha': 'EICAR Test String',
        'eicar.lzh': 'EICAR Test String',
        'eicar.msc': 'EICAR Test String',
        'eicar.plain': 'EICAR Test String',
        'eicar.rar': 'EICAR Test String',
        'eicar.tar': 'EICAR Test String',
        'eicar.uue': 'EICAR Test String',
        'eicar.zip': 'EICAR Test String',
        'eicar_arj.bin': 'EICAR Test String',
        'eicar_cab.bin': 'EICAR Test String',
        'eicar_gz.bin': 'EICAR Test String',
        'eicar_lha.bin': 'EICAR Test String',
        'eicar_lzh.bin': 'EICAR Test String',
        'eicar_mime.bin': 'EICAR Test String',
        'eicar_msc.bin': 'EICAR Test String',
        'eicar_niveau1.zip': 'EICAR Test String',
        'eicar_niveau10.zip': None,
        'eicar_niveau11.zip': None,
        'eicar_niveau12.zip': None,
        'eicar_niveau13.zip': None,
        'eicar_niveau14.bin': None,
        'eicar_niveau14.jpg': None,
        'eicar_niveau2.zip': 'EICAR Test String',
        'eicar_niveau3.zip': None,
        'eicar_niveau30.bin': None,
        'eicar_niveau30.rar': None,
        'eicar_niveau4.zip': None,
        'eicar_niveau5.zip': None,
        'eicar_niveau6.zip': None,
        'eicar_niveau7.zip': None,
        'eicar_niveau8.zip': None,
        'eicar_niveau9.zip': None,
        'eicar_rar.bin': 'EICAR Test String',
        'eicar_tar.bin': 'EICAR Test String',
        'eicar_uu.bin': 'EICAR Test String',
        'eicarhqx_binhex.bin': 'EICAR Test String',
    }

    antivirus_class = Symantec


if __name__ == '__main__':
    unittest.main()
