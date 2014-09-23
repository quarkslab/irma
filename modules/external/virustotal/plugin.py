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


class VirusTotalPlugin(PluginBase):

    class VirusTotalResult:
        ERROR = -1
        FOUND = 1
        NOT_FOUND = 0

    # =================
    #  plugin metadata
    # =================

    _plugin_name_ = "VirusTotal"
    _plugin_author_ = "IRMA (c) Quarkslab"
    _plugin_version_ = "1.0.0"
    _plugin_category_ = IrmaProbeType.external
    _plugin_description_ = "Plugin to query VirusTotal API"
    _plugin_dependencies_ = [
        ModuleDependency(
            'virus_total_apis',
            help='See requirements.txt for needed dependencies'
        ),
        FileDependency(
            os.path.join(os.path.dirname(__file__), 'config.ini')
        )
    ]

    # =============
    #  constructor
    # =============

    def __init__(self, apikey=None, private=None):
        # load default configuration file
        config = SafeConfigParser()
        config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))

        # override default values if specified
        if apikey is None:
            self.apikey = config.get('VirusTotal', 'apikey')
        else:
            self.apikey = apikey

        if private is None:
            self.private = bool(config.get('VirusTotal', 'private'))
        else:
            self.private = private

        # choose either public or private API for requests
        if private:
            module = sys.modules['virus_total_apis'].PrivateApi
        else:
            module = sys.modules['virus_total_apis'].PublicApi
        self.module = module(self.apikey)

    def get_file_report(self, filename):
        with open(filename, 'rb') as filedesc:
            digest = hashlib.md5(filedesc.read()).hexdigest()
        return self.module.get_file_report(digest)

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
            response = self.get_file_report(paths)
            stopped = timestamp(datetime.utcnow())
            results.duration = stopped - started
            # check eventually for errors
            if 'error' in response:
                results.status = self.VirusTotalResult.ERROR
                results.error = "Network probably unreachable"
            elif (response['response_code'] == 204) or \
                 (response['response_code'] == 403):
                results.status = self.VirusTotalResult.ERROR
                results.error = response['results']['verbose_msg']
            elif (response['response_code'] == 200) and \
                 (response['results']['response_code'] != 1):
                results.status = self.VirusTotalResult.NOT_FOUND
            else:
                results.status = self.VirusTotalResult.FOUND
            results.results = response if 'error' not in response else None
        except Exception as e:
            results.status = self.VirusTotalResult.ERROR
            results.results = str(e)
        return results
