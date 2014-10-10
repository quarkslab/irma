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

from datetime import datetime

from lib.common.utils import timestamp
from lib.plugins import PluginBase
from lib.plugin_result import PluginResult
from lib.irma.common.utils import IrmaProbeType
from lib.plugins.exceptions import PluginLoadError


class SkeletonPlugin(PluginBase):

    class SkeletonResult:
        ERROR = -1
        FAILURE = 0
        SUCCESS = 1

    # =================
    #  plugin metadata
    # =================
    _plugin_name_ = "Skeleton"
    _plugin_author_ = "<author name>"
    _plugin_version_ = "<version>"
    _plugin_category_ = "custom"
    _plugin_description_ = "Plugin skeleton"
    _plugin_dependencies_ = []

    # =============
    #  constructor
    # =============

    def __init__(self):
        pass

    @classmethod
    def verify(cls):
        raise PluginLoadError("Skeleton plugin is not meant to be loaded")

    # ==================
    #  probe interfaces
    # ==================
    def run(self, paths):
        response = PluginResult(name=type(self).plugin_name,
                                type=type(self).plugin_category,
                                version=None)
        try:
            started = timestamp(datetime.utcnow())
            response.results = "Main analysis call here"
            stopped = timestamp(datetime.utcnow())
            response.duration = stopped - started
            response.status = self.SkeletonResult.SUCCESS
        except Exception as e:
            response.status = self.SkeletonResult.ERROR
            response.results = str(e)
        return response
