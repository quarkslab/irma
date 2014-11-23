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
import sys
import hashlib

from ConfigParser import SafeConfigParser
from datetime import datetime

from lib.common.utils import timestamp
from lib.plugins import PluginBase
from lib.plugins import ModuleDependency, FileDependency
from lib.plugin_result import PluginResult
from lib.irma.common.utils import IrmaProbeType


class YaraPlugin(PluginBase):

    class YaraResult:
        ERROR = -1
        FOUND = 1
        NOT_FOUND = 0

    # =================
    #  plugin metadata
    # =================

    _plugin_name_ = "Yara"
    _plugin_author_ = "Bryan Nolen @BryanNolen"
    _plugin_version_ = "1.0.0"
    _plugin_category_ = IrmaProbeType.metadata
    _plugin_description_ = "Plugin to run files against yara rules"
    _plugin_dependencies_ = [
        ModuleDependency(
            'yara',
            help='Requires yara 3 or greater and matching yara-python'
        ),
        FileDependency(
            os.path.join(os.path.dirname(__file__), 'config.ini')
        )
    ]

    # =============
    #  constructor
    # =============

    def __init__(self, rule_path=None):
        # load default configuration file
        config = SafeConfigParser()
        config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))

        # override default values if specified
        if rule_path is None:
            self.rule_path = config.get('Yara', 'rule_path')
        else:
            self.rule_path = rule_path

        self.rules = sys.modules['yara'].compile(filepath=self.rule_path)

    def get_file_report(self, filename):
        try:
            results = (False, self.rules.match(filename, timeout=60))
        except Exception as e:
            results = (True, str(e))
        finally:
            return results

    # ==================
    #  probe interfaces
    # ==================

    def run(self, paths):
        results = PluginResult(name=type(self).plugin_name,
                               type=type(self).plugin_category,
                               version=None)
        try:
            # get the report, automatically append results
            started = timestamp(datetime.utcnow())
            (error_raised, response) = self.get_file_report(paths)
            stopped = timestamp(datetime.utcnow())
            results.duration = stopped - started
            # check eventually for errors
            if error_raised:
                results.status = self.YaraResult.ERROR
                results.error = response
            elif response.__len__() == 0:
                results.status = self.YaraResult.NOT_FOUND
            else:
                results.status = self.YaraResult.FOUND
            match_string = ""
            matches = []
            if results.status is self.YaraResult.FOUND:
                for match in response:
                    match_string = "{0}, {1}".format(match_string, match)
                    matches.append("{0!s}".format(match))
            #results.results = {'Matches': "{0}".format(match_string)} if not error_raised else None
            results.results = {'Matches': matches} if not error_raised else None
        except Exception as e:
            results.status = self.YaraResult.ERROR
            results.results = str(e)
        return results
