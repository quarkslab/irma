import logging
import unittest

from tests.antivirus.common import GenericEicar
from modules.antivirus.zoner.zoner import Zoner


# ============
#  Test Cases
# ============

class ZonerEicar(GenericEicar, unittest.TestCase):

    expected_results = {
        'eicar-passwd.zip': None,
        'eicar.arj': 'EICAR.Test.File-NoVirus',
        'eicar.cab': 'EICAR.Test.File-NoVirus',
        'eicar.com.pgp': None,
        'eicar.com.txt': 'EICAR.Test.File-NoVirus',
        'eicar.lha': 'EICAR.Test.File-NoVirus',
        'eicar.lzh': 'EICAR.Test.File-NoVirus',
        'eicar.msc': 'EICAR.Test.File-NoVirus',
        'eicar.plain': 'EICAR.Test.File-NoVirus',
        'eicar.rar': 'EICAR.Test.File-NoVirus',
        'eicar.tar': None,
        'eicar.uue': None,
        'eicar.zip': 'EICAR.Test.File-NoVirus',
        'eicar_arj.bin': 'EICAR.Test.File-NoVirus',
        'eicar_cab.bin': 'EICAR.Test.File-NoVirus',
        'eicar_gz.bin': 'EICAR.Test.File-NoVirus',
        'eicar_lha.bin': 'EICAR.Test.File-NoVirus',
        'eicar_lzh.bin': 'EICAR.Test.File-NoVirus',
        'eicar_mime.bin': None,
        'eicar_msc.bin': 'EICAR.Test.File-NoVirus',
        'eicar_niveau1.zip': 'EICAR.Test.File-NoVirus',
        'eicar_niveau10.zip': 'EICAR.Test.File-NoVirus',
        'eicar_niveau11.zip': 'EICAR.Test.File-NoVirus',
        'eicar_niveau12.zip': 'EICAR.Test.File-NoVirus',
        'eicar_niveau13.zip': 'EICAR.Test.File-NoVirus',
        'eicar_niveau14.bin': 'EICAR.Test.File-NoVirus',
        'eicar_niveau14.jpg': 'EICAR.Test.File-NoVirus',
        'eicar_niveau2.zip': 'EICAR.Test.File-NoVirus',
        'eicar_niveau3.zip': 'EICAR.Test.File-NoVirus',
        'eicar_niveau30.bin': 'EICAR.Test.File-NoVirus',
        'eicar_niveau30.rar': 'EICAR.Test.File-NoVirus',
        'eicar_niveau4.zip': 'EICAR.Test.File-NoVirus',
        'eicar_niveau5.zip': 'EICAR.Test.File-NoVirus',
        'eicar_niveau6.zip': 'EICAR.Test.File-NoVirus',
        'eicar_niveau7.zip': 'EICAR.Test.File-NoVirus',
        'eicar_niveau8.zip': 'EICAR.Test.File-NoVirus',
        'eicar_niveau9.zip': 'EICAR.Test.File-NoVirus',
        'eicar_rar.bin': 'EICAR.Test.File-NoVirus',
        'eicar_tar.bin': None,
        'eicar_uu.bin': None,
        'eicarhqx_binhex.bin': None,
    }

    antivirus_class = Zoner


if __name__ == '__main__':
    unittest.main()
