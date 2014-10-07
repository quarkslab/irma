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

import re
import os
import sys
import logging

from datetime import datetime
from lib.common.utils import timestamp
from lib.plugins import PluginBase
from lib.plugins import ModuleDependency
from lib.plugin_result import PluginResult
from lib.irma.common.utils import IrmaProbeType


class PEAnalyzerPlugin(PluginBase):

    class StaticAnalyzerResults:
        ERROR = -1
        SUCCESS = 1
        FAILURE = 0

    # =================
    #  plugin metadata
    # =================

    _plugin_name_ = "StaticAnalyzer"
    _plugin_author_ = "IRMA (c) Quarkslab"
    _plugin_version_ = "1.0.0"
    _plugin_category_ = IrmaProbeType.metadata
    _plugin_description_ = "Plugin to analyze PE files"
    _plugin_dependencies_ = [
        ModuleDependency(
            'pefile',
            help='See requirements.txt for needed dependencies'
        ),
        ModuleDependency(
            'peutils',
            help='See requirements.txt for needed dependencies'
        ),
        ModuleDependency(
            'modules.metadata.pe_analyzer.pe'
        ),
        ModuleDependency(
            'lib.common.mimetypes'
        ),
    ]

    # ==================================
    #  constructor and destructor stuff
    # ==================================

    def __init__(self):
        module = sys.modules['modules.metadata.pe_analyzer.pe'].PE
        self.module = module()

    def analyze(self, filename):
        # check parameters
        if not filename:
            raise RuntimeError("filename is invalid")
        # check if file exists
        mimetype = None
        if os.path.exists(filename):
            # guess mimetype for file
            magic = sys.modules['lib.common.mimetypes'].Magic
            mimetype = magic.from_file(filename)
        else:
            raise RuntimeError("file does not exist")
        result = None
        # look for PE mime type
        if mimetype and re.match('PE32', mimetype):
            result = self.module.analyze(filename)
        else:
            logging.warning("{0} not yet handled".format(mimetype))
        return result

    def run(self, paths):
        results = PluginResult(name=type(self).plugin_name,
                               type=type(self).plugin_category,
                               version=None)
        # launch file analysis
        try:
            started = timestamp(datetime.utcnow())
            response = self.analyze(filename=paths)
            stopped = timestamp(datetime.utcnow())
            results.duration = stopped - started
            # update results
            if not response:
                results.status = self.StaticAnalyzerResults.FAILURE
                results.results = "Not a PE file"
            else:
                results.status = self.StaticAnalyzerResults.SUCCESS
                results.results = response
        except Exception as e:
            results.status = self.StaticAnalyzerResult.ERROR
            results.error = str(e)
        return results
