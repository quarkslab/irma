import os
import sys
import logging

from sys import platform

from .manager import PluginManager
from .exceptions import PluginError
from .exceptions import PluginLoadError
from .exceptions import PluginFormatError
from .exceptions import PluginCrashed
from .exceptions import DependencyMissing
from .exceptions import ModuleDependencyMissing
from .exceptions import BinaryDependencyMissing
from .exceptions import FileDependencyMissing
from .exceptions import FolderDependencyMissing
from .exceptions import PlatformDependencyMissing


##############################################################################
# Plugin
##############################################################################

class PluginMetaClass(type):

    ##########################################################################
    # Plugin metadata
    ##########################################################################

    _plugin_name_ = ''
    _plugin_display_name_ = ''
    _plugin_author_ = ''
    _plugin_version_ = None
    _plugin_description_ = ''
    _plugin_dependencies_ = []
    _plugin_category_ = ''
    _plugin_active_ = None
    _plugin_mimetype_regexp = None

    ##########################################################################
    # Plugin methods
    ##########################################################################

    def __init__(cls, name, bases, attrs):
        # small hack to skip PluginBase class when initializing
        if not len(attrs):
            return
        # perform some verifications
        if not cls._plugin_name_:
            raise PluginFormatError("Invalid plugin_name")
        if not cls._plugin_display_name_:
            raise PluginFormatError("Invalid plugin_display_name")
        if not cls._plugin_author_:
            raise PluginFormatError("Invalid plugin_author")
        if not cls._plugin_version_:
            raise PluginFormatError("Invalid plugin_version")
        if not cls._plugin_category_:
            raise PluginFormatError("Invalid plugin_category")
        # try to register plugin
        PluginManager().register_plugin(cls)

    ##########################################################################
    # Plugin getters and setters
    ##########################################################################

    @property
    def plugin_name(cls):
        return cls._plugin_name_

    @property
    def plugin_display_name(cls):
        return cls._plugin_display_name_

    @property
    def plugin_version(cls):
        return cls._plugin_version_

    @property
    def plugin_description(cls):
        return cls._plugin_description_

    @property
    def plugin_dependencies(cls):
        return cls._plugin_dependencies_

    @property
    def plugin_category(cls):
        return cls._plugin_category_

    @property
    def plugin_active(cls):
        return cls._plugin_active_

    @plugin_active.setter
    def plugin_active(cls, value):
        cls._plugin_active_ = bool(value)

    @property
    def plugin_canonical_name(cls):
        if hasattr(cls, '_plugin_canonical_name_'):
            return str(cls._plugin_canonical_name_)
        return '.'.join([cls.__module__ + cls.__class__.__name__])

    @property
    def plugin_path(cls):
        return sys.modules[cls.__module__].__file__

    @property
    def plugin_mimetype_regexp(cls):
        return cls._plugin_mimetype_regexp

# Metaclass compatible with python 2 and 3. Inherit from this for Plugins
PluginBase = PluginMetaClass('PluginBase', (object,), {})
