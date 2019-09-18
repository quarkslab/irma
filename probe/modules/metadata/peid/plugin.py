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

from configparser import ConfigParser
from datetime import datetime

from irma.common.utils.utils import timestamp
from irma.common.plugins import PluginBase
from irma.common.plugin_result import PluginResult
from irma.common.base.utils import IrmaProbeType
from irma.common.plugins import ModuleDependency, FileDependency
from irma.common.plugins import PluginLoadError


class PEiDPlugin(PluginBase):

    class PEiDResult:
        ERROR = -1
        FOUND = 1
        NOT_FOUND = 0

    # =================
    #  plugin metadata
    # =================

    _plugin_name_ = "PEiD"
    _plugin_display_name_ = "PEiD PE Packer Identifier"
    _plugin_author_ = "Quarkslab"
    _plugin_version_ = "1.0.0"
    _plugin_category_ = IrmaProbeType.metadata
    _plugin_description_ = "Plugin to run files against PEiD signatures"
    _plugin_dependencies_ = [
        ModuleDependency(
            'pefile',
            help='See requirements.txt for needed dependencies'
        ),
        ModuleDependency(
            'peutils',
            help='See requirements.txt for needed dependencies'
        ),
        FileDependency(
            os.path.join(os.path.dirname(__file__), 'config.ini')
        )
    ]
    _plugin_mimetype_regexp = 'PE32'

    @classmethod
    def verify(cls):
        # load default configuration file
        config = ConfigParser()
        config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
        sign_path = config.get('PEiD', 'sign_path')

        # check for configured signatures path
        if not os.path.exists(sign_path):
            raise PluginLoadError("{0}: verify() failed because "
                                  "signatures file not found."
                                  "".format(cls.__name__))
    # =============
    #  constructor
    # =============

    def __init__(self):
        config = ConfigParser()
        config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
        sign_path = config.get('PEiD', 'sign_path')
        peutils = sys.modules['peutils']
        data = open(sign_path, "r", encoding="utf8", errors="ignore").read()
        self.signatures = peutils.SignatureDatabase(data=data)

    def analyze(self, filename):
        pefile = sys.modules['pefile']
        try:
            pe = pefile.PE(filename)
            results = self.signatures.match(pe)
            if results is None:
                return self.PEiDResult.NOT_FOUND, "No match found"
            else:
                return self.PEiDResult.FOUND, results[0]
        except pefile.PEFormatError:
            return self.PEiDResult.NOT_FOUND, "Not a PE"

    # ==================
    #  probe interfaces
    # ==================

    def run(self, paths):
        results = PluginResult(name=type(self).plugin_display_name,
                               type=type(self).plugin_category,
                               version=None)
        try:
            started = timestamp(datetime.utcnow())
            (status, response) = self.analyze(paths)
            stopped = timestamp(datetime.utcnow())
            results.duration = stopped - started
            results.status = status
            results.results = response
        except Exception as e:
            results.status = self.PEiDResult.ERROR
            results.error = type(e).__name__ + " : " + str(e)
        return results
