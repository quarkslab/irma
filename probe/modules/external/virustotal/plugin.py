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
from irma.common.plugins import ModuleDependency, FileDependency
from irma.common.plugin_result import PluginResult
from irma.common.base.utils import IrmaProbeType
from irma.common.utils.hash import md5sum


class VirusTotalPlugin(PluginBase):

    class VirusTotalResult:
        ERROR = -1
        FOUND = 1
        NOT_FOUND = 0

    # =================
    #  plugin metadata
    # =================

    _plugin_name_ = "VirusTotal"
    _plugin_display_name_ = "VirusTotal"
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
        config = ConfigParser()
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
            digest = md5sum(filedesc)
        return self.module.get_file_report(digest)

    # ==================
    #  probe interfaces
    # ==================

    def run(self, paths):
        results = PluginResult(name=type(self).plugin_display_name,
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
                results.error = str(response['error'])
            elif response['response_code'] == 204:
                results.status = self.VirusTotalResult.ERROR
                results.error = "Public API request rate limit exceeded"
            elif response['response_code'] == 403:
                results.status = self.VirusTotalResult.ERROR
                results.error = "Access forbidden (wrong key value or type)"
            elif response['response_code'] == 200 and \
                 response['results']['response_code'] != 1:
                results.status = self.VirusTotalResult.NOT_FOUND
            else:
                results.status = self.VirusTotalResult.FOUND
            results.results = response if 'error' not in response else None
        except Exception as e:
            results.status = self.VirusTotalResult.ERROR
            results.results = type(e).__name__ + " : " + str(e)
        return results
