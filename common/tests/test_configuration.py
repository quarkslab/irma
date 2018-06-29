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
import os
import copy
from irma.common.configuration.config import ConfigurationSection
from irma.common.configuration.ini import IniConfiguration, \
    TemplatedConfiguration
from irma.common.configuration.sql import SQLConf
from irma.common.base.exceptions import IrmaConfigurationError


# =================
#  Logging options
# =================
def enable_logging(level=logging.INFO, handler=None, formatter=None):
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
class TestIniConfiguration(unittest.TestCase):

    def test_ini_config_value(self):
        directory = os.path.dirname(os.path.realpath(__file__))
        config = IniConfiguration("{0}/test.ini".format(directory))
        self.assertEqual(config["foo"].bar, "foobar")
        self.assertEqual(config["foo bar"].foo, "foo")
        self.assertEqual(config["foo bar"].bar, "bar")

    def test_ini_config_types(self):
        directory = os.path.dirname(os.path.realpath(__file__))
        config = IniConfiguration("{0}/test.ini".format(directory))
        self.assertEqual(isinstance(config, IniConfiguration),
                         True)
        self.assertEqual(isinstance(config["foo bar"], ConfigurationSection),
                         True)
        self.assertEqual(isinstance(config["foo bar"].bar, str),
                         True)


template = {'foo':
            [('bar', TemplatedConfiguration.string, None)],
            'foo bar':
            [('foo', TemplatedConfiguration.string, None),
             ('bar', TemplatedConfiguration.string, None),
             ('val', TemplatedConfiguration.integer, 1337)],
            'bar':
            [('foo1', TemplatedConfiguration.integer, 42),
             ('foo2', TemplatedConfiguration.string, "Answer"),
             ('foo3', TemplatedConfiguration.boolean, None),
             ('foo4', TemplatedConfiguration.boolean, False)
             ]
            }


class TestTemplatedConfiguration(unittest.TestCase):

    def test_templated_config_value(self):
        directory = os.path.dirname(os.path.realpath(__file__))
        template_path = "{0}/test.ini".format(directory)
        config = TemplatedConfiguration(template_path, template)
        self.assertTrue(isinstance(config, TemplatedConfiguration))
        self.assertEqual(config["foo"].bar, "foobar")
        self.assertEqual(config["foo bar"].foo, "foo")
        self.assertEqual(config["foo bar"].bar, "bar")
        self.assertEqual(config["bar"].foo1, 65)
        self.assertTrue(config["bar"].foo3)

    def test_templated_config_default_value(self):
        directory = os.path.dirname(os.path.realpath(__file__))
        template_path = "{0}/test.ini".format(directory)
        config = TemplatedConfiguration(template_path, template)
        self.assertEqual(config["foo bar"].val, 1337)
        self.assertEqual(config["bar"].foo2, "Answer")
        self.assertFalse(config["bar"].foo4)

    def test_templated_config_missing_value(self):
        directory = os.path.dirname(os.path.realpath(__file__))
        template1 = copy.copy(template)
        template1['missingsection'] = [
            ('missingkey', TemplatedConfiguration.string, None)]
        with self.assertRaises(IrmaConfigurationError):
            TemplatedConfiguration("{0}/test.ini".format(directory), template1)

    def test_templated_config_section_only_default_value(self):
        directory = os.path.dirname(os.path.realpath(__file__))
        template1 = copy.copy(template)
        template1['missingsection'] = [
            ('missingkey', TemplatedConfiguration.string, "with_def_value")]
        config = TemplatedConfiguration("{0}/test.ini".format(directory),
                                        template1)
        self.assertTrue(isinstance(config["missingsection"],
                                   ConfigurationSection))
        self.assertEqual(config["missingsection"].missingkey,
                         "with_def_value")

    def test_templated_config_value_with_space(self):
        directory = os.path.dirname(os.path.realpath(__file__))
        template1 = copy.copy(template)
        template1['missingsection'] = [
            ('one missing key',
             TemplatedConfiguration.string,
             "with_def_value")]
        config = TemplatedConfiguration("{0}/test.ini".format(directory),
                                        template1)
        self.assertTrue(isinstance(config["missingsection"],
                                   ConfigurationSection))
        self.assertEqual(config["missingsection"]["one missing key"],
                         "with_def_value")

    def test_templated_config_wrong_template_tuple_instead_of_list(self):
        directory = os.path.dirname(os.path.realpath(__file__))
        template1 = copy.copy(template)
        template1['missingsection'] = (('key',
                                        TemplatedConfiguration.string,
                                        None))
        with self.assertRaises(IrmaConfigurationError):
            TemplatedConfiguration("{0}/test.ini".format(directory), template1)

    def test_templated_config_wrong_value(self):
        directory = os.path.dirname(os.path.realpath(__file__))
        template_path = "{0}/test.ini".format(directory)
        template1 = copy.copy(template)
        template1['WrongVal'] = [('an_int',
                                  TemplatedConfiguration.integer,
                                  None)]
        with self.assertRaises(IrmaConfigurationError):
            TemplatedConfiguration(template_path, template1)


class TestSQLConf(unittest.TestCase):

    def test_url(self):
        conf = SQLConf(dbms='dbms', dialect='dialect', username='username',
                       password='password', host='host', port='port',
                       dbname='dbname')

        self.assertEqual(conf.url,
                         'dbms+dialect://username:password@host:port/dbname')

        conf.dialect = None
        conf.port = None
        conf.password = None
        self.assertEqual(conf.url, 'dbms://username@host/dbname')

        conf.username = None
        self.assertEqual(conf.url, 'dbms://host/dbname')

        conf.host = None
        self.assertEqual(conf.url, 'dbms:///dbname')


if __name__ == '__main__':
    enable_logging()
    unittest.main()
