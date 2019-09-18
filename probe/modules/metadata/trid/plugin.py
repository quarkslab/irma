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

from datetime import datetime
from irma.common.utils.utils import timestamp
from irma.common.plugins import PluginBase
from irma.common.plugins import FileDependency
from irma.common.plugins import PlatformDependency
from irma.common.plugin_result import PluginResult


class TrIDPlugin(PluginBase):

    class TrIDResults:
        ERROR = -1
        FAILURE = 0
        SUCCESS = 1

    _plugin_name_ = "TrID"
    _plugin_display_name_ = "TrID File Identifier"
    _plugin_author_ = "IRMA (c) Quarkslab"
    _plugin_version_ = "1.0.0"
    _plugin_category_ = "metadata"
    _plugin_description_ = "Plugin to determine file type"
    _plugin_dependencies_ = [
        PlatformDependency('linux'),
        FileDependency(
            os.path.join('/opt/trid/', 'trid'),
            help='Make sure you have downloaded trid binary'
        ),
        FileDependency(
            os.path.join('/opt/trid/', 'triddefs.trd'),
            help='Make sure to have downloaded trid definitions'
        ),
    ]

    def __init__(self):
        module = sys.modules['modules.metadata.trid.trid'].TrID
        self.module = module()

    def run(self, paths):
        results = PluginResult(name=type(self).plugin_display_name,
                               type=type(self).plugin_category,
                               version=None)
        # launch file analysis
        try:
            started = timestamp(datetime.utcnow())
            results.status, results.results = self.module.analyze(paths)
            stopped = timestamp(datetime.utcnow())
            results.duration = stopped - started
        except Exception as e:
            results.status = self.TrIDResults.ERROR
            results.error = type(e).__name__ + " : " + str(e)
        return results
