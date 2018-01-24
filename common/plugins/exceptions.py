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


import traceback


##############################################################################
# Plugin Exceptions
##############################################################################

class PluginError(Exception):

    def __init__(self, value=None):
        self.value = value or ""


class PluginLoadError(PluginError):

    def __init__(self, value=None):
        super(PluginLoadError, self).__init__(value)

    def __str__(self):
        return '{reason}'.format(reason=self.value)


class PluginFormatError(PluginLoadError):

    def __init__(self, value):
        super(PluginFormatError, self).__init__(value)

    def __str__(self):
        return 'format error ({reason})'.format(reason=self.value)


class PluginCrashed(PluginError):

    def __init__(self, value):
        super(PluginCrashed, self).__init__(value)

    def __str__(self):
        return 'crashed ({reason})'.format(reason=self.value)


##############################################################################
# Dependency Exceptions
##############################################################################

class DependencyMissing(PluginLoadError):

    def __init__(self, value=None, dependency=None):
        super(DependencyMissing, self).__init__(value)
        self.dependency = None or dependency

    def __str__(self):
        return "missing dependency: {dependency}" \
               "".format(dependency=self.dependency)


class ModuleDependencyMissing(DependencyMissing):
    pass


class BinaryDependencyMissing(DependencyMissing):
    pass


class FileDependencyMissing(DependencyMissing):
    pass


class FolderDependencyMissing(DependencyMissing):
    pass


class PlatformDependencyMissing(DependencyMissing):
    pass
