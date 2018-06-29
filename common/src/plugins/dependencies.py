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

from importlib import import_module
from functools import reduce

try:  # from python3, shutil has a which like command
    from shutil import which
except ImportError:
    from irma.common.plugins.which import which


##############################################################################
# Plugin imports
##############################################################################

from irma.common.plugins.exceptions import PluginError, PluginCrashed
from irma.common.plugins.exceptions import PluginLoadError, PluginFormatError

from irma.common.plugins.exceptions import DependencyMissing
from irma.common.plugins.exceptions import ModuleDependencyMissing
from irma.common.plugins.exceptions import BinaryDependencyMissing
from irma.common.plugins.exceptions import FileDependencyMissing
from irma.common.plugins.exceptions import FolderDependencyMissing
from irma.common.plugins.exceptions import PlatformDependencyMissing


##############################################################################
# Dependency
##############################################################################

class Dependency(object):

    exception = DependencyMissing

    def __init__(self, dependency_name, help=None):
        self.dependency_name = dependency_name
        self.help = help
        self._was_satisfied = None

    def is_satisfied(self):
        raise NotImplementedError

    def satisfied(self):
        # _was_satisfied is the cached value for is_satisfied()
        satisfied = getattr(self, '_was_satisfied')
        if not satisfied:
            self._was_satisfied = self.is_satisfied()
        return self._was_satisfied

    def check(self):
        if not self.satisfied():
            raise self.exception(dependency=self)


class ModuleDependency(Dependency):

    exception = ModuleDependencyMissing

    def is_satisfied(self):
        if self.dependency_name in sys.modules:
            return True
        try:
            import_module(self.dependency_name)
            return True
        except Exception:
            return False


class BinaryDependency(Dependency):

    exception = BinaryDependencyMissing

    def is_satisfied(self):
        if isinstance(self.dependency_name, list):
            dependency_found = [which(x) for x in self.dependency_name]
            return reduce(lambda x, y: x or y, dependency_found, False)
        else:
            return which(self.dependency_name) is not None

    def __str__(self):
        return self.dependency_name


class FileDependency(Dependency):

    exception = FileDependencyMissing

    def is_satisfied(self):
        return os.path.exists(self.dependency_name) and \
            os.path.isfile(self.dependency_name)


class FolderDependency(Dependency):

    exception = FolderDependencyMissing

    def is_satisfied(self):
        return os.path.exists(self.dependency_name) and \
            os.path.isdir(self.dependency_name)


class PlatformDependency(Dependency):

    exception = PlatformDependencyMissing

    def is_satisfied(self):
        dependencies = self.dependency_name
        if not isinstance(dependencies, list):
            dependencies = [dependencies]
        for platform in dependencies:
            if sys.platform.startswith(platform):
                return True
        return False
