#
# Copyright (c) 2013-2018 Quarkslab.
# This file is part of IRMA project.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License in the top-level directory
# of this distribution and at:
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# No part of the project, including this file, may be copied,
# modified, propagated, or distributed except according to the
# terms contained in the LICENSE file.

import logging
import unittest
from irma.common.utils.utils import UUID, MAC
from irma.common.base.utils import IrmaFrontendReturn, IrmaTaskReturn, \
    IrmaReturnCode


# =================
#  Logging options
# =================

def enable_logging(level=logging.INFO, handler=None, formatter=None):
    global log
    log = logging.getLogger()
    if formatter is None:
        formatter = logging.Formatter("%(asctime)s [%(name)s] " +
                                      "%(levelname)s: %(message)s")
    if handler is None:
        handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.setLevel(level)


# ============
#  Test Cases
# ============

class TestCommonUtils(unittest.TestCase):

    def test_uuid(self):
        uuid = UUID.generate()
        self.assertTrue(UUID.validate(uuid))
        self.assertEqual(len(uuid), 36)
        self.assertEqual(uuid.count("-"), 4)

    def test_uuid_generate(self):
        uuid = UUID.normalize("01234567-abcd-ef01-2345-deadbeaff00d")
        self.assertTrue(UUID.validate(uuid))
        self.assertEqual(uuid, "01234567-abcd-ef01-2345-deadbeaff00d")

    def test_uuid_validate(self):
        self.assertFalse(UUID.validate("not a uuid"))

    def test_mac(self):
        mac = MAC.generate()
        self.assertTrue(MAC.validate(mac))
        self.assertEqual(len(mac), 17)
        self.assertEqual(mac.count(":"), 5)

    def test_mac_generate(self):
        mac = MAC.generate(oui=[0x12, 0x34, 0x56])
        mac = MAC.normalize(mac)
        self.assertTrue(MAC.validate(mac))
        self.assertTrue(mac.startswith("12:34:56"))

    def test_mac_validate(self):
        self.assertFalse(MAC.validate("not a mac"))

    def test_irma_taskreturn_success(self):
        ret = IrmaTaskReturn.success("success")
        self.assertEqual(ret[0],
                         IrmaReturnCode.success)
        self.assertEqual(ret[1],
                         "success")
        self.assertEqual(type(ret),
                         tuple)
        self.assertEqual(type(ret[0]),
                         int)
        self.assertEqual(type(ret[1]),
                         str)

    def test_irma_taskreturn_warning(self):
        ret = IrmaTaskReturn.warning("warning")
        self.assertEqual(ret[0],
                         IrmaReturnCode.warning)
        self.assertEqual(ret[1],
                         "warning")
        self.assertEqual(type(ret),
                         tuple)
        self.assertEqual(type(ret[0]),
                         int)
        self.assertEqual(type(ret[1]),
                         str)

    def test_irma_taskreturn_error(self):
        ret = IrmaTaskReturn.error("error")
        self.assertEqual(ret[0],
                         IrmaReturnCode.error)
        self.assertEqual(ret[1],
                         "error")
        self.assertEqual(type(ret),
                         tuple)
        self.assertEqual(type(ret[0]),
                         int)
        self.assertEqual(type(ret[1]),
                         str)

    def test_irma_frontendreturn_success(self):
        f_success = IrmaFrontendReturn.success
        ret = f_success(optional={'key': 'value'})
        self.assertEqual(ret['code'],
                         IrmaReturnCode.success)
        self.assertEqual(ret['msg'],
                         "success")
        self.assertEqual(type(ret),
                         dict)
        self.assertEqual(type(ret['code']),
                         int)
        self.assertEqual(type(ret['msg']),
                         str)
        self.assertEqual(type(ret['optional']),
                         dict)
        self.assertEqual(ret['optional']['key'],
                         'value')

    def test_irma_frontendreturn_warning(self):
        f_warning = IrmaFrontendReturn.warning
        ret = f_warning("warning", optional={'key': 'value'})
        self.assertEqual(ret['code'],
                         IrmaReturnCode.warning)
        self.assertEqual(ret['msg'],
                         "warning")
        self.assertEqual(type(ret),
                         dict)
        self.assertEqual(type(ret['code']),
                         int)
        self.assertEqual(type(ret['msg']),
                         str)
        self.assertEqual(type(ret['optional']),
                         dict)
        self.assertEqual(ret['optional']['key'],
                         'value')

    def test_irma_frontendreturn_error(self):
        f_error = IrmaFrontendReturn.error
        ret = f_error("error", optional={'key': 'value'})
        self.assertEqual(ret['code'],
                         IrmaReturnCode.error)
        self.assertEqual(ret['msg'],
                         "error")
        self.assertEqual(type(ret),
                         dict)
        self.assertEqual(type(ret['code']),
                         int)
        self.assertEqual(type(ret['msg']),
                         str)
        self.assertEqual(type(ret['optional']),
                         dict)
        self.assertEqual(ret['optional']['key'],
                         'value')


if __name__ == '__main__':
    enable_logging()
    unittest.main()
