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

import re
import os
import sys
import logging


from datetime import datetime
from irma.common.utils.utils import timestamp
from irma.common.plugins import PluginBase
from irma.common.plugins import ModuleDependency
from irma.common.plugin_result import PluginResult
from irma.common.base.utils import IrmaProbeType
from irma.common.utils.mimetypes import Magic


class LiefAnalyzerPlugin(PluginBase):

    class LiefAnalyzerResult:
        ERROR = -1
        FAILURE = 0
        SUCCESS = 1

    # =================
    #  plugin metadata
    # =================
    _plugin_name_ = "LIEF"
    _plugin_display_name_ = "LIEF"
    _plugin_author_ = "Romain Thomas"
    _plugin_version_ = "1.0.0"
    _plugin_category_ = IrmaProbeType.metadata
    _plugin_description_ = "Plugin using LIEF to analyze binaries"
    _plugin_dependencies_ = [
        ModuleDependency(
            'lief',
            help='See requirements.txt for needed dependencies'
        ),
        ModuleDependency(
            'modules.metadata.lief.lief_analyzer'
        ),
    ]
    _plugin_mimetype_regexp = "ELF|PE32"

    # =============
    #  constructor
    # =============

    def __init__(self):
        lief_module = sys.modules[
            'modules.metadata.lief.lief_analyzer'].LIEFAnalyzer
        self.module = lief_module()
        self.lief_version = self.module.get_version()

    # ==================
    #  probe interfaces
    # ==================
    def analyze(self, filename):
        # check parameters
        if not filename:
            raise RuntimeError("filename is invalid")
        # check if file exists
        mimetype = None
        if os.path.exists(filename):
            # guess mimetype for file
            mimetype = Magic.from_file(filename)
        else:
            raise RuntimeError("file does not exist")
        result = None
        if mimetype and re.match(self._plugin_mimetype_regexp, mimetype):
            result = self.module.analyze(filename)
        else:
            logging.warning("{0} not yet handled".format(mimetype))

        return result

    def run(self, paths):
        results = PluginResult(name=type(self).plugin_name,
                               type=type(self).plugin_category,
                               version=self.lief_version)
        try:
            started = timestamp(datetime.utcnow())
            response = self.analyze(filename=paths)
            stopped = timestamp(datetime.utcnow())

            results.duration = stopped - started
            # update results
            if not response:
                results.status = self.LiefAnalyzerResult.FAILURE
                results.results = "ERROR"
            else:
                results.status = self.LiefAnalyzerResult.SUCCESS
                results.results = response
        except Exception as e:
            results.status = self.LiefAnalyzerResult.ERROR
            results.results = type(e).__name__ + " : " + str(e)
        return results
