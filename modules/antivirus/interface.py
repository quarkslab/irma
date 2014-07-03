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
import hashlib

from lib.plugin_result import PluginResult


class AntivirusPluginInterface(object):
    """Antivirus Plugin"""

    def run(self, paths, heuristic=None):
        # allocate plugin results place-holders
        plugin_results = PluginResult(type(self).plugin_name)
        # launch an antivirus scan, automatically append scan results to
        # antivirus.results.
        plugin_results.start_time = None
        plugin_results.result_code = self.module.scan(paths, heuristic)
        plugin_results.end_time = None
        # allocate memory for data, and fill with data
        plugin_results.data = dict()
        plugin_results.data['name'] = self.module.name
        plugin_results.data['version'] = self.module.version
        plugin_results.data['database'] = dict()
        # calculate database metadata
        if self.module.database:
            for filename in self.module.database:
                database = plugin_results.data['database']
                database[filename] = self.file_metadata(filename)
        plugin_results.data['scan_results'] = self.module.scan_results
        return plugin_results.serialize()

    @staticmethod
    def file_metadata(filename):
        result = dict()
        if os.path.exists(filename):
            result['mtime'] = os.path.getmtime(filename)
            result['ctime'] = os.path.getctime(filename)
            with open(filename, 'rb') as fd:
                result['sha256'] = hashlib.sha256(fd.read()).hexdigest()
        return result
