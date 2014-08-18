#
# Copyright (c) 2013-2014 QuarksLab.
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

import os
import logging
import libvirt
import unittest

from ..virt.core.connection import ConnectionManager


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


# ===========================
#  Test Cases for Connection
# ===========================

class CheckConnectionManager(unittest.TestCase):

    def setUp(self):
        dirname = os.path.dirname(os.path.realpath(__file__))
        filepath = os.path.join(dirname, "node.xml")
        self.uri = "test://{0}".format(filepath)

    def test_constructor(self):
        cm = ConnectionManager(self.uri)
        self.assertIsNotNone(cm)

    def test_with(self):
        with ConnectionManager(self.uri) as cm:
            pass

    def test_version(self):
        with ConnectionManager(self.uri) as cm:
            self.assertIsNotNone(cm.version)
            self.assertEquals(len(cm.version), 3)
            self.assertIsInstance(cm.version, tuple)

    def test_create_uri(self):
        with self.assertRaises(NotImplementedError):
            with ConnectionManager(self.uri) as cm:
                cm.create_uri("dummy")

    def test_uri(self):
        with ConnectionManager(self.uri) as cm:
            self.assertEquals(cm.uri, self.uri)

    def test_connection(self):
        with ConnectionManager(self.uri) as cm:
            self.assertIsNotNone(cm.connection)
            self.assertIsInstance(cm.connection, libvirt.virConnect)

    def test_reconnect(self):
        # test with an inexisting connection (not cached)
        with ConnectionManager(self.uri) as cm:
            cm._drv = None
            self.assertIsNotNone(cm.connection)
            self.assertIsInstance(cm.connection, libvirt.virConnect)
        # test with an existing connection (already cached)
        with ConnectionManager(self.uri) as cmo:
            # call version to force call to connect()
            version = cmo.version
            cmo._drv = None
            with ConnectionManager(self.uri) as cmi:
                version = cmi.version
                self.assertIsNotNone(cmi.connection)
                self.assertIsInstance(cmi.connection, libvirt.virConnect)

if __name__ == '__main__':
    enable_logging()
    unittest.main()
