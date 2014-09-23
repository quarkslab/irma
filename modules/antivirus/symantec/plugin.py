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

from .symantec import Symantec
from ..interface import AntivirusPluginInterface

from lib.plugins import PluginBase, PluginLoadError
from lib.plugins import BinaryDependency, PlatformDependency
from lib.irma.common.utils import IrmaProbeType


class SymantecPlugin(PluginBase, Symantec, AntivirusPluginInterface):

    # =================
    #  plugin metadata
    # =================

    _plugin_name_ = "Symantec"
    _plugin_author_ = "IRMA (c) Quarkslab"
    _plugin_version_ = "1.0.0"
    _plugin_category_ = IrmaProbeType.antivirus
    _plugin_description_ = "Plugin for Symantec Antivirus on Windows"
    _plugin_dependencies_ = [
        PlatformDependency('win32')
    ]

    @classmethod
    def verify(cls):
        module = Symantec()
        if not module.scan_path or not os.path.exists(module.scan_path):
            del module
            raise PluginLoadError("Unable to find Symantec executable")
        del module

    # =============
    #  constructor
    # =============

    def __init__(self):
        # load default configuration file
        self.module = Symantec()
