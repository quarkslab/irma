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
import sys
import pkgutil
import logging

from lib.common.oopatterns import Singleton

##############################################################################
# Plugin imports
##############################################################################

from .exceptions import PluginError, PluginCrashed
from .exceptions import PluginLoadError, PluginFormatError
from .exceptions import DependencyMissing
from .exceptions import ModuleDependencyMissing, BinaryDependencyMissing
from .exceptions import FileDependencyMissing, FolderDependencyMissing

from .dependencies import Dependency
from .dependencies import ModuleDependency, BinaryDependency
from .dependencies import FileDependency, FolderDependency, PlatformDependency


class PluginManager(Singleton):

    __plugins_cls = {}

    ##########################################################################
    # plugin management
    ##########################################################################

    def get_all_plugins(self):
        return self.__plugins_cls.values()

    def discover(self, path=os.path.dirname(__file__), prefix=None):
        dirname = os.path.basename(path)
        if prefix is None:
            prefix = dirname
        for importer, name, ispkg in pkgutil.walk_packages([path]):
            try:
                pkg_name = '%s.%s' % (prefix, name)
                if pkg_name not in sys.modules:
                    module_meta = importer.find_module(name)
                    module = module_meta.load_module(pkg_name)
                else:
                    module = sys.modules[pkg_name]
                if ispkg:
                    self.discover(os.path.join(path, name), pkg_name)
            except PluginFormatError as error:
                logging.warn(' *** [{name}] Plugin error: {error}'
                             ''.format(name=name, error=error))
            except PluginLoadError as error:
                logging.warn(' *** [{name}] Plugin failed to load: {error}'
                             ''.format(name=name, error=error))
            except PluginCrashed as error:
                logging.warn(' *** [{name}] Plugin crashed: {error}'
                             ''.format(name=name, error=error))
            except ImportError as error:
                logging.exception(error)

    ##########################################################################
    # plugin registering
    ##########################################################################

    def register_plugin(cls, plugin):
        logging.debug('Found plugin {name}. Trying to register it.'
                      ''.format(name=plugin.plugin_name))
        # if required, run additionnal verifications on the plugin
        if hasattr(plugin, 'verify'):
            if not plugin.verify():
                logging.warn("Conditions not met for plugin {name}"
                             "".format(name=plugin.__name__))
                raise PluginLoadError('Conditions not verified')
        # check for dependencies
        for dependency in plugin.plugin_dependencies:
            try:
                dependency.check()
            except DependencyMissing as error:
                # get plugin info
                plugin_name = plugin.plugin_name
                # get dependency info
                dependency = error.dependency
                dependency_name = dependency.dependency_name
                dependency_type = dependency.__class__.__name__
                dependency_help = dependency.help
                # warn user and stop loading
                warning = '{type} not satisfied: {name} -> {deps}.'
                if dependency_help is not None:
                    warning += ' {help}'
                logging.warn(warning.format(type=dependency_type,
                                            name=plugin_name,
                                            deps=dependency_name,
                                            help=dependency_help))
                return
        # add plugin to internal list
        if plugin.plugin_canonical_name in cls.__plugins_cls:
            logging.debug('Plugin {plugin} already registered'
                          ''.format(plugin=plugin.plugin_name))
        else:
            cls.__plugins_cls[plugin.plugin_canonical_name] = plugin
            # mark plugin as active
            if plugin.plugin_active is None:
                plugin.plugin_active = True
            logging.debug('Plugin {name} registered, active set as {state}'
                          ''.format(name=plugin.plugin_name,
                                    state=plugin.plugin_active))
