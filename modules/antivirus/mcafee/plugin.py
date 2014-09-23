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

from .vscl import McAfeeVSCL
from ..interface import AntivirusPluginInterface

from lib.plugins import PluginBase, PluginLoadError
from lib.irma.common.utils import IrmaProbeType


class McAfeeVSCLPlugin(PluginBase, McAfeeVSCL, AntivirusPluginInterface):

    # =================
    #  plugin metadata
    # =================

    _plugin_name_ = "McAfeeVSCL"
    _plugin_author_ = "IRMA (c) Quarkslab"
    _plugin_version_ = "1.0.0"
    _plugin_category_ = IrmaProbeType.antivirus
    _plugin_description_ = "Plugin for McAfee VirusScan Command Line " \
                           "(VSCL) scanner"
    _plugin_dependencies_ = []

    @classmethod
    def verify(cls):
        # create an instance
        module = McAfeeVSCL()
        path = module.scan_path
        del module
        # perform checks
        if not path or not os.path.exists(path):
            raise PluginLoadError("{0}: verify() failed because "
                                  "McAfeeVSCL executable was not found."
                                  "".format(cls.__name__))

    # =============
    #  constructor
    # =============

    def __init__(self):
        # load default configuration file
        self.module = McAfeeVSCL()
