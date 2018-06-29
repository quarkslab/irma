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

"""Defines common Object Oriented Patterns

One should re-use these instead of defining their owns.
"""


# ==========================
#  Singleton Design Pattern
# ==========================

class SingletonMetaClass(type):
    """Metaclass for singleton design pattern.

    .. warning::

            This metaclass should not be used directly. To declare a class
            using the singleton pattern, one should use the :class:`Singleton`
            class instead.

    """

    _instances = {}

    def __call__(mcs, *args, **kwargs):
        if mcs not in mcs._instances:
            mcs._instances[mcs] = \
                super(SingletonMetaClass, mcs).__call__(*args, **kwargs)
        return mcs._instances[mcs]


# Metaclass compatible with python 2 and 3. Inherit from this for singletons
Singleton = SingletonMetaClass('Singleton', (object,), {})
"""Base class for singleton

This class implements the singleton design pattern. One can inherit from this
base class to make a class implement the singleton design pattern.

    .. code-block:: python

        # a class implementing a singleton
        class aParametricSingleton(Singleton):

            # do some stuff here
            pass

        # let us verify that it is really a singleton
        print(id(aParametricSingleton())
        print(id(aParametricSingleton())

"""


# =====================================
#  Parametric Singleton Design Pattern
# =====================================

class ParametricSingletonMetaClass(type):
    """Metaclass for parametric singleton design pattern

    .. warning::

            This metaclass should not be used directly. To declare a class
            using the singleton pattern, one should use the
            :class:`ParametricSingleton` class instead and precise the
            parameter used for the dict using a class method named
            ``depends_on``.

    """

    _instances = {}

    def __call__(mcs, *args, **kwargs):
        # check for "depends_on" attribute
        if "depends_on" not in kwargs and not hasattr(mcs, "depends_on"):
            raise TypeError("argument or attribute 'depends_on' not defined")
        # check for unbound methods
        if "depends_on" in kwargs and \
           (not kwargs["depends_on"] or not callable(kwargs["depends_on"])):
            raise TypeError("function in parameter 'depends_on' is not bound")
        elif hasattr(mcs, "depends_on") and \
            (not getattr(mcs, "depends_on") or
             not callable(getattr(mcs, "depends_on"))):
            raise TypeError("function in attribute 'depends_on' is not bound")

        # call depends_on to get the key
        if "depends_on" in kwargs:
            key = kwargs["depends_on"](mcs, args, kwargs)
            del kwargs["depends_on"]
        else:
            key = getattr(mcs, "depends_on")(mcs, args, kwargs)

        # check for instance
        if mcs not in mcs._instances:
            mcs._instances[mcs] = {}
        if key not in mcs._instances[mcs]:
            mcs._instances[mcs][key] = \
                super(ParametricSingletonMetaClass, mcs).\
                __call__(*args, **kwargs)
        return mcs._instances[mcs][key]

    def update_key(mcs, old_key, new_key):
        mcs._instances[mcs][new_key] = mcs._instances[mcs].pop(old_key)

    def remove_key(mcs, key):
        if key in mcs._instances:
            del mcs._instances[mcs][key]


# Metaclass compatible with python 2 and 3.
# Inherit from this for parametric singletons
ParametricSingleton = ParametricSingletonMetaClass('ParametricSingleton',
                                                   (object,), {})
"""Base class for parametric singletons

This class implements the parametric singleton design pattern. One can inherit
from this base class to make a class implement a parametric singleton pattern.
Pass either an argument ``depends_on`` in the constructor or define a class
method called ``depends_on`` that specifies how to compute the parameter value
used for the hash table storing the instances:

* example with a **static method**:

.. code-block:: python

    class aParametricSingleton(ParametricSingleton):

        @staticmethod
        def depends_on(*args, **kwargs):
            return "my key"

* example with a **``lambda`` wrapped with a static method**:

.. code-block:: python

    class aParametricSingleton(ParametricSingleton):

        depends_on = staticmethod(lambda *args, **kwargs: "my key")
"""


class PluginMetaClass(type):
    """Metaclass for auto-registering plugin pattern

    .. warning::

            This metaclass should not be used directly. To declare a class
            using the plugin pattern, one should use the :class:`Plugin`
            class instead.

    """

    # ===================
    #  class constructor
    # ===================
    def __init__(mcs, name, bases, attrs):
        # small hack to skip Plugin base class when initializing
        if not len(attrs):
            return
        # Begin to register all classes that derives from Plugin base class
        if not hasattr(mcs, '_plugins'):
            # This branch only executes when processing the mount point itself.
            # So, since this is a new plugin type, not an implementation, this
            # class shouldn't be registered as a plugin. Instead, it sets up a
            # list where plugins can be registered later.
            mcs._plugins = []
        else:
            # This must be a plugin implementation, which should be registered.
            # Simply appending it to the list is all that's needed to keep
            # track of it later.
            mcs._plugins.append(mcs)

    # =================
    #  Plugin metadata
    # =================

    _plugin_name = None
    _plugin_version = None
    _plugin_description = None
    _plugin_dependencies = None

    # =====================
    #  Setters and getters
    # =====================

    @property
    def plugin_name(mcs):
        return mcs._plugin_name

    @property
    def plugin_version(mcs):
        return mcs._plugin_version

    @property
    def plugin_description(mcs):
        return mcs._plugin_description

    @property
    def plugin_dependencies(mcs):
        return mcs._plugin_dependencies

    @property
    def plugins(mcs):
        return mcs._plugins

    # =================
    #  Utility methods
    # =================

    def get_plugins(mcs, *args, **kwargs):
        """return instances of plugins"""
        return [plugin(*args, **kwargs) for plugin in mcs._plugins]

    def get_plugin(mcs, name, *args, **kwargs):
        """return instance of a named plugin"""
        plugin = [x for x in mcs._plugins if x.plugin_name == name]
        return plugin[0] if plugin else None


# Metaclass compatible with python 2 and 3. Inherit from this for Plugins
Plugin = PluginMetaClass('Plugin', (object,), {})
