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

from datetime import datetime

from irma.common.utils.utils import timestamp
from irma.common.plugins import PluginBase
from irma.common.plugin_result import PluginResult
from irma.common.base.utils import IrmaProbeType
from irma.common.plugins import FileDependency
from irma.common.plugins import PlatformDependency
from irma.common.utils.hash import sha256sum


class DummyPlugin(PluginBase):

    class DummyResult:
        ERROR = -1
        FAILURE = 0
        SUCCESS = 1

    # =================
    #  plugin metadata
    # =================
    _plugin_name_ = "Dummy"
    _plugin_display_name_ = "Dummy"
    _plugin_author_ = "IRMA (c) Quarkslab"
    _plugin_version_ = "0.0.1"
    _plugin_category_ = IrmaProbeType.metadata
    _plugin_description_ = "Plugin to return SHA256 of a file"
    _plugin_dependencies_ = [
        PlatformDependency('linux'),
        FileDependency(
            '/opt/Dummy_probe_activated',
            help='Make sure you have activated the Dummy probe'
        ),
    ]

    # =============
    #  constructor
    # =============

    def __init__(self):
        pass

    # ==================
    #  probe interfaces
    # ==================
    def run(self, paths):
        response = PluginResult(name=type(self).plugin_display_name,
                                type=type(self).plugin_category,
                                version=None)
        try:
            started = timestamp(datetime.utcnow())
            response.results = sha256sum(open(paths, 'rb'))
            stopped = timestamp(datetime.utcnow())
            response.duration = stopped - started
            response.status = self.DummyResult.SUCCESS
        except Exception as e:
            response.status = self.DummyResult.ERROR
            response.results = type(e).__name__ + " : " + str(e)
        return response
