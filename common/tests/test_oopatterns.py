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

from irma.common.utils.oopatterns import Singleton, ParametricSingleton, Plugin


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


# ==========================
#  Test Cases for Singleton
# ==========================

class CheckSingleton(unittest.TestCase):

    def test_simple_singleton(self):
        # define simple classes
        class SingletonClass(Singleton):
            pass

        a = SingletonClass()
        b = SingletonClass()
        self.assertEqual(id(a), id(b))

    def test_inheritance_singleton(self):
        # define simple classes
        class SingletonClass(Singleton):
            pass

        class InheritedSingletonClass(SingletonClass):
            pass

        a = SingletonClass()
        b = InheritedSingletonClass()
        self.assertNotEqual(id(a), id(b))


# ====================================
#  Test Cases for ParametricSingleton
# ====================================

class CheckParametricSingleton(unittest.TestCase):

    def test_simple_singleton_with_identical_param(self):
        # define inner classes
        class ParametricSingletonClass1(ParametricSingleton):
            @classmethod
            def depends_on(*args, **kwargs):
                return ParametricSingletonClass1.__name__

        class ParametricSingletonClass2(ParametricSingleton):
            depends_on = classmethod(lambda x, *y, **z: x.__name__)

        # Perform checks
        a = ParametricSingletonClass1()
        key = ParametricSingletonClass1.__name__
        b = ParametricSingletonClass1(depends_on=lambda x, *y, **z: key)
        self.assertEqual(id(a), id(b))

        a = ParametricSingletonClass2()
        key = ParametricSingletonClass2.__name__
        b = ParametricSingletonClass2(depends_on=lambda x, *y, **z: key)
        self.assertEqual(id(a), id(b))

    def test_inheritance_singleton(self):
        # define inner classes
        class ParametricSingleton1(ParametricSingleton):
            @classmethod
            def depends_on(*args, **kwargs):
                return ParametricSingleton1.__name__

        class InheritedParametricSingleton1(ParametricSingleton1):
            pass

        class ParametricSingleton2(ParametricSingleton):
            depends_on = classmethod(lambda x, *y, **z: x.__name__)

        class InheritedParametricSingleton2(ParametricSingleton2):
            pass

        # Perform checks
        a = ParametricSingleton1()
        key = ParametricSingleton1.__name__
        b = InheritedParametricSingleton1(depends_on=lambda x, *y, **z: key)
        self.assertNotEqual(id(a), id(b))

        a = ParametricSingleton2()
        key = ParametricSingleton2.__name__
        b = InheritedParametricSingleton2(depends_on=lambda x, *y, **z: key)
        self.assertNotEqual(id(a), id(b))

    def test_inheritance_singleton_with_identical_param(self):
        # define inner classes
        class ParametricSingleton1(ParametricSingleton):
            @classmethod
            def depends_on(cls, *args, **kwargs):
                return cls.__name__

        class InheritedParametricSingleton1(ParametricSingleton1):
            pass

        class ParametricSingleton2(ParametricSingleton):
            depends_on = classmethod(lambda x, *y, **z: x.__name__)

        class InheritedParametricSingleton2(ParametricSingleton2):
            pass

        # Perform checks
        a = ParametricSingleton1()
        b = InheritedParametricSingleton1()
        self.assertNotEqual(id(a), id(b))

        key = ParametricSingleton1.__name__
        a = ParametricSingleton1(depends_on=lambda x, *y, **z: key)
        # use the same key to check if the is not collision
        b = InheritedParametricSingleton1(depends_on=lambda x, *y, **z: key)
        self.assertNotEqual(id(a), id(b))

        a = ParametricSingleton2()
        b = InheritedParametricSingleton2()
        self.assertNotEqual(id(a), id(b))

        key = ParametricSingleton2.__name__
        a = ParametricSingleton2(depends_on=lambda x, *y, **z: key)
        # use the same key to check if the is not collision
        b = InheritedParametricSingleton2(depends_on=lambda x, *y, **z: key)
        self.assertNotEqual(id(a), id(b))

    def test_inheritance_singleton_with_different_param(self):
        # define inner classes
        class ParametricSingleton1(ParametricSingleton):
            @classmethod
            def depends_on(*args, **kwargs):
                return ParametricSingleton1.__name__

        class InheritedParametricSingleton1(ParametricSingleton1):
            pass

        class ParametricSingleton2(ParametricSingleton):
            depends_on = classmethod(lambda x, *y, **z: x.__name__)

        class InheritedParametricSingleton2(ParametricSingleton2):
            pass

        # Perform checks
        a = ParametricSingleton1()
        key = InheritedParametricSingleton1.__name__
        b = InheritedParametricSingleton1(depends_on=lambda x, *y, **z: key)
        self.assertNotEqual(id(a), id(b))

        a = ParametricSingleton1(depends_on=lambda x, *y, **z: x.__name__)
        key = InheritedParametricSingleton1.__name__
        b = InheritedParametricSingleton1(depends_on=lambda x, *y, **z: key)
        self.assertNotEqual(id(a), id(b))

        a = ParametricSingleton2()
        key = InheritedParametricSingleton2.__name__
        b = InheritedParametricSingleton2(depends_on=lambda x, *y, **z: key)
        self.assertNotEqual(id(a), id(b))

        a = ParametricSingleton2(depends_on=lambda x, *y, **z: x.__name__)
        key = InheritedParametricSingleton2.__name__
        b = InheritedParametricSingleton2(depends_on=lambda x, *y, **z: key)
        self.assertNotEqual(id(a), id(b))

    def test_depends_on_errors(self):
        # depends_on not defined
        with self.assertRaises(TypeError):
            class ParametricSingleton1(ParametricSingleton):
                pass
            obj = ParametricSingleton1()

        # depends_on not callable
        with self.assertRaises(TypeError):
            class ParametricSingleton1(ParametricSingleton):
                depends_on = True
            obj = ParametricSingleton1()

        # kwargs['depends_on'] not callable
        with self.assertRaises(TypeError):
            class ParametricSingleton1(ParametricSingleton):
                pass
            obj = ParametricSingleton1(depends_on=True)

    def test_update_key(self):

        class ParametricSingleton1(ParametricSingleton):
            pass

        obj1 = ParametricSingleton1(depends_on=lambda x, *y, **z: "key1")
        self.assertIsNotNone(obj1)
        # move key1 to key2
        ParametricSingleton1.update_key("key1", "key2")
        # create a new key1
        obj2 = ParametricSingleton1(depends_on=lambda x, *y, **z: "key1")
        self.assertIsNotNone(obj2)
        self.assertNotEqual(id(obj1), id(obj2))
        # create a new key2 and check
        obj3 = ParametricSingleton1(depends_on=lambda x, *y, **z: "key2")
        self.assertIsNotNone(obj3)
        self.assertEqual(id(obj1), id(obj3))
        self.assertNotEqual(id(obj2), id(obj3))


# ========================
#  Test Cases for Plugins
# ========================

class PluginGroup(Plugin):
    pass


class PluginOne(PluginGroup):
    # define meta
    _plugin_name = "plugin1 name"
    _plugin_version = "plugin1 version"
    _plugin_description = "plugin1 description"
    _plugin_dependencies = "plugin1 deps"


class PluginTwo(PluginGroup):
    # define meta
    _plugin_name = "plugin2 name"
    _plugin_version = "plugin2 version"
    _plugin_description = "plugin2 description"
    _plugin_dependencies = "plugin2 deps"


class CheckPlugin(unittest.TestCase):

    def test_plugin_name(self):
        # define simple classes
        self.assertEqual(PluginOne.plugin_name, "plugin1 name")
        self.assertEqual(PluginTwo.plugin_name, "plugin2 name")

    def test_plugin_version(self):
        # define simple classes
        self.assertEqual(PluginOne.plugin_version, "plugin1 version")
        self.assertEqual(PluginTwo.plugin_version, "plugin2 version")

    def test_plugin_description(self):
        # define simple classes
        self.assertEqual(PluginOne.plugin_description, "plugin1 description")
        self.assertEqual(PluginTwo.plugin_description, "plugin2 description")

    def test_plugin_dependencies(self):
        # define simple classes
        self.assertEqual(PluginOne.plugin_dependencies, "plugin1 deps")
        self.assertEqual(PluginTwo.plugin_dependencies, "plugin2 deps")

    def test_plugins(self):
        # get plugins
        self.assertEqual(len(PluginGroup.plugins), 2)
        self.assertTrue(PluginOne in PluginGroup.plugins)
        self.assertTrue(PluginTwo in PluginGroup.plugins)

    def test_get_plugin(self):
        self.assertEqual(PluginGroup.get_plugin("plugin1 name"), PluginOne)
        self.assertEqual(PluginGroup.get_plugin("plugin2 name"), PluginTwo)
        self.assertIsNone(PluginGroup.get_plugin("unknown"))

    def test_get_plugins(self):
        plugins = PluginGroup.get_plugins()
        for plugin in plugins:
            is_one = isinstance(plugin, PluginOne)
            is_two = isinstance(plugin, PluginTwo)
            self.assertTrue(is_one or is_two)


if __name__ == '__main__':
    enable_logging()
    unittest.main()
