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

from irma.common.plugins import PluginBase
from irma.common.base.utils import IrmaProbeType


class AntivirusFormatterPlugin(PluginBase):

    # =================
    #  plugin metadata
    # =================

    _plugin_name_ = "AntivirusDefault"
    _plugin_display_name_ = _plugin_name_
    _plugin_author_ = "IRMA (c) Quarkslab"
    _plugin_version_ = "1.0.0"
    _plugin_category_ = IrmaProbeType.antivirus
    _plugin_description_ = "Default Formatter for Antivirus category"
    _plugin_dependencies_ = []

    # ===========
    #  Formatter
    # ===========

    @staticmethod
    def can_handle_results(raw_result):
        # New probe result format (from version 1.0.4)
        return raw_result.get('type', None) == IrmaProbeType.antivirus

    @staticmethod
    def format(raw_result):
        # New probe result format (from version 1.0.4)
        # As the raw_result has almost the same structure as the json for the
        # output, we simply delete antivirus specific fields and we return the
        # object
        raw_result.pop('database', None)
        return raw_result
