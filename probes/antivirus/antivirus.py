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

import logging
import os
import hashlib

from lib.common.oopatterns import Plugin
from lib.plugin_result import PluginResult
from probes.processing import Processing
from probes.information.system import System

log = logging.getLogger(__name__)


class AntivirusProbe(Plugin, Processing):

    ##########################################################################
    # plugin metadata
    ##########################################################################

    _plugin_name = None
    _plugin_version = None
    _plugin_description = None
    _plugin_dependencies = [
        System,  # append system information
    ]

    ##########################################################################
    # Helpers
    ##########################################################################

    @staticmethod
    def file_metadata(filename):
        result = dict()
        if os.path.exists(filename):
            result['mtime'] = os.path.getmtime(filename)
            result['ctime'] = os.path.getctime(filename)
            with open(filename, 'rb') as fd:
                result['sha256'] = hashlib.sha256(fd.read()).hexdigest()
        return result

    ##########################################################################
    # processing interface
    ##########################################################################

    def __init__(self, conf=None, **kwargs):
        # store configuration
        self._conf = conf
        self._module = None

    def ready(self):
        result = False
        if super(AntivirusProbe, self).ready():
            if self._module.scan_path and \
               os.path.exists(self._module.scan_path):
                if os.path.isfile(self._module.scan_path):
                    result = True
        return result

    # TODO: create an object to hold antivirus data instead of a dict
    def run(self, paths, heuristic=None):
        # allocate plugin results place-holders
        plugin_results = PluginResult(type(self).plugin_name)
        # launch an antivirus scan, automatically append scan results to
        # antivirus.results.
        plugin_results.start_time = None
        plugin_results.result_code = self._module.scan(paths, heuristic)
        plugin_results.end_time = None
        # allocate memory for data, and fill with data
        plugin_results.data = dict()
        plugin_results.data['name'] = self._module.name
        plugin_results.data['version'] = self._module.version
        plugin_results.data['database'] = dict()
        # calculate database metadata
        if self._module.database:
            for filename in self._module.database:
                database = plugin_results.data['database']
                database[filename] = self.file_metadata(filename)
        plugin_results.data['scan_results'] = self._module.scan_results
        # append dependency data
        if type(self).plugin_dependencies:
            for dependency in type(self).plugin_dependencies:
                plugin_results.add_dependency_data(dependency().run())
        return plugin_results.serialize()
