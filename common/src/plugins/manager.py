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

import os
import sys
import pkgutil
import logging

from irma.common.utils.oopatterns import Singleton

##############################################################################
# Plugin imports
##############################################################################

from irma.common.plugins.exceptions import PluginError, PluginCrashed, \
    PluginLoadError, PluginFormatError, DependencyMissing, \
    ModuleDependencyMissing, BinaryDependencyMissing, FileDependencyMissing, \
    FolderDependencyMissing
from irma.common.plugins.dependencies import Dependency, ModuleDependency, \
    BinaryDependency, FileDependency, FolderDependency, PlatformDependency


class PluginManager(Singleton):

    __plugins_cls = {}

    ##########################################################################
    # plugin management
    ##########################################################################

    def get_all_plugins(self):
        return list(self.__plugins_cls.values())

    def discover(self, path=os.path.dirname(__file__), prefix=None):
        dirname = os.path.basename(path)
        if prefix is None:
            prefix = dirname
        for importer, name, ispkg in pkgutil.walk_packages([path]):
            try:
                pkg_name = '%s.%s' % (prefix, name)
                if pkg_name not in sys.modules:
                    __import__(pkg_name)
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
    @classmethod
    def register_plugin(cls, plugin):
        logging.debug('Found plugin {name}. Trying to register it.'
                      ''.format(name=plugin.plugin_name))
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
                warning = '{name} miss dependencies: {deps} ({type}).'
                if dependency_help is not None:
                    warning += ' {help}'
                raise PluginLoadError(warning.format(type=dependency_type,
                                                     name=plugin_name,
                                                     deps=dependency_name,
                                                     help=dependency_help))
        # if required, run additionnal verifications on the plugin
        if hasattr(plugin, 'verify'):
            try:
                plugin.verify()
            except Exception as error:
                raise PluginLoadError(error)
        # add plugin to internal list
        if plugin.plugin_canonical_name in cls.__plugins_cls:
            logging.debug('Plugin {name} already registered'
                          ''.format(name=plugin.plugin_name))
        else:
            cls.__plugins_cls[plugin.plugin_canonical_name] = plugin
            # mark plugin as active
            if plugin.plugin_active is None:
                plugin.plugin_active = True
            logging.debug('Plugin {name} registered, active set as {state}'
                          ''.format(name=plugin.plugin_name,
                                    state=plugin.plugin_active))
