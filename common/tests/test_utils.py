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
from unittest.mock import Mock, patch
from irma.common.utils.utils import UUID, bytes_to_utf8, save_to_file
from irma.common.base.utils import IrmaFrontendReturn, IrmaTaskReturn, \
    IrmaReturnCode, IrmaScanStatus, IrmaValueError, common_celery_options, \
    IrmaScanRequest, IrmaProbeType


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

    def test_bytes_to_utf8_0(self):
        result = bytes_to_utf8(b"something")
        self.assertEqual(result, "something")

    def test_bytes_to_utf8_1(self):
        result = bytes_to_utf8("something")
        self.assertIs(result, "something")

    def test_bytes_to_utf8_2(self):
        result = bytes_to_utf8(["foo", b"bar", (b"baz",)])
        self.assertEqual(result, ["foo", "bar", ("baz",)])

    def test_bytes_to_utf8_3(self):
        result = bytes_to_utf8({"foo": b"bar", b"baz": None})
        self.assertDictEqual(result, {"foo": "bar", "baz": None})

    @patch("builtins.open")
    def test_save_to_file0(self, m_open):
        Mockfile = type("Mockfile", (Mock, ),
                        {"seek": lambda self, pos: setattr(self, "pos", pos)})
        fileobj = Mockfile()
        fileobj.read.return_value = ""
        fileobj.pos = 0

        dstobj = Mockfile()
        m_open.return_value.__enter__.return_value = dstobj

        size = save_to_file(fileobj, "/foo")

        m_open.assert_called_once_with("/foo", "wb")
        self.assertEqual(fileobj.pos, 0)
        self.assertEqual(size, 0)
        dstobj.write.assert_not_called()

    @patch("builtins.open")
    def test_save_to_file1(self, m_open):
        Mockfile = type("Mockfile", (Mock, ),
                        {"seek": lambda self, pos: setattr(self, "pos", pos),
                         "write": lambda self, buf: setattr(
                                  self, "written", self.written + buf)})
        fileobj = Mockfile()
        fileobj.read.side_effect = ["foo", "bar", "baz", ""]
        fileobj.pos = 0

        dstobj = Mockfile()
        dstobj.written = ""
        m_open.return_value.__enter__.return_value = dstobj

        size = save_to_file(fileobj, "/foo")

        m_open.assert_called_once_with("/foo", "wb")
        self.assertEqual(dstobj.written, "foobarbaz")
        self.assertEqual(fileobj.pos, 0)
        self.assertEqual(size, 9)

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

    def test_irmascanstatus_is_error0(self):
        self.assertFalse(IrmaScanStatus.is_error(IrmaScanStatus.finished))

    def test_irmascanstatus_is_error1(self):
        self.assertTrue(IrmaScanStatus.is_error(IrmaScanStatus.error))

    def test_irmascanstatus_is_error2(self):
        self.assertTrue(IrmaScanStatus.is_error(IrmaScanStatus.error_probe_na))

    def test_irmascanstatus_filter_status0(self):
        mini, maxi = IrmaScanStatus.launched, IrmaScanStatus.flushed
        self.assertIs(IrmaScanStatus.filter_status(
            IrmaScanStatus.processed, mini, maxi), None)

    def test_irmascanstatus_filter_status1(self):
        mini, maxi = IrmaScanStatus.launched, IrmaScanStatus.flushed
        with self.assertRaises(IrmaValueError):
            IrmaScanStatus.filter_status(IrmaScanStatus.ready, mini, maxi)

    def test_irmascanstatus_filter_status2(self):
        mini, maxi = IrmaScanStatus.launched, IrmaScanStatus.flushed
        with self.assertRaises(IrmaValueError):
            IrmaScanStatus.filter_status(IrmaScanStatus.cancelled, mini, maxi)

    def test_irmascanstatus_filter_status3(self):
        mini, maxi = IrmaScanStatus.launched, IrmaScanStatus.flushed
        with self.assertRaises(IrmaValueError):
            IrmaScanStatus.filter_status(25, mini, maxi)

    def test_irmascanstatus_code_ot_label0(self):
        self.assertEqual(
                IrmaScanStatus.code_to_label(IrmaScanStatus.finished),
                "finished")

    def test_irmascanstatus_code_ot_label1(self):
        self.assertEqual(
                IrmaScanStatus.code_to_label(25),
                "Unknown status code")

    def test_irmaprobetype_normalize0(self):
        self.assertEqual(
                IrmaProbeType.normalize("external"),
                IrmaProbeType.external)

    def test_irmaprobetype_normalize1(self):
        self.assertEqual(
                IrmaProbeType.normalize("foo"),
                IrmaProbeType.unknown)

    @patch("irma.common.base.utils.UUID.generate")
    def test_common_celery_options0(self, m_generate):
        m_generate.return_value = "a-random-uuid"

        result = common_celery_options("foo", "bar", 0, 50, 100)
        self.assertEqual(result, [
            "--app=foo",
            "--loglevel=info",
            "--without-gossip",
            "--without-mingle",
            "--without-heartbeat",
            "--soft-time-limit=50",
            "--time-limit=100",
            "--hostname=bar-a-random-uuid"])

    @patch("irma.common.base.utils.UUID.generate")
    def test_common_celery_options1(self, m_generate):
        m_generate.return_value = "a-random-uuid"

        result = common_celery_options("foo", "bar", 3, 50, 100)
        self.assertEqual(result, [
            "--app=foo",
            "--loglevel=info",
            "--without-gossip",
            "--without-mingle",
            "--without-heartbeat",
            "--concurrency=3",
            "--soft-time-limit=50",
            "--time-limit=100",
            "--hostname=bar-a-random-uuid"])


class TestIrmaScanRequest(unittest.TestCase):

    def setUp(self):
        self.isr = IrmaScanRequest()

    def test_init(self):
        isr = IrmaScanRequest({"foo": Mock(), "bar": Mock()})
        self.assertEqual(isr.nb_files, 2)

    def test_add_file(self):
        self.isr.add_file("foo", "probelist", "mimetype")
        self.assertDictEqual(
                self.isr.request["foo"],
                {"probe_list": "probelist", "mimetype": "mimetype"})
        self.assertEqual(self.isr.nb_files, 1)

    def test_del_file0(self):
        self.isr.add_file("foo", "probelist", "mimetype")
        self.isr.del_file("foo")
        self.assertNotIn("foo", self.isr.request)
        self.assertEqual(self.isr.nb_files, 0)

    def test_del_file1(self):
        self.isr.del_file("foo")
        self.assertNotIn("foo", self.isr.request)
        self.assertEqual(self.isr.nb_files, 0)

    def test_get_probelist(self):
        self.isr.add_file("foo", "bar", "mimetype")
        result = self.isr.get_probelist("foo")
        self.assertEqual(result, "bar")
        self.assertEqual(self.isr.nb_files, 1)

    def test_set_probelist(self):
        self.isr.add_file("foo", "bar", "mimetype")
        self.isr.set_probelist("foo", "baz")
        self.assertEqual(self.isr.get_probelist("foo"), "baz")
        self.assertEqual(self.isr.nb_files, 1)

    def test_get_mimetype(self):
        self.isr.add_file("foo", "probelist", "bar")
        result = self.isr.get_mimetype("foo")
        self.assertEqual(result, "bar")
        self.assertEqual(self.isr.nb_files, 1)

    def test_to_dict(self):
        self.assertIs(self.isr.request, self.isr.to_dict())

    def test_files(self):
        self.assertEqual(self.isr.request.keys(), self.isr.files())


if __name__ == '__main__':
    enable_logging()
    unittest.main()
