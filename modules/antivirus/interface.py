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

from datetime import datetime
from lib.common.utils import timestamp
from lib.plugin_result import PluginResult


class AntivirusPluginInterface(object):
    """Antivirus Plugin"""

    def run(self, paths):
        results = PluginResult(name=self.module.name,
                               type=type(self).plugin_category,
                               version=self.module.version)
        try:
            # add database metadata
            results.database = None
            if self.module.database:
                results.database = dict()
                for filename in self.module.database:
                    results.database[filename] = self.file_metadata(filename)
            # launch an antivirus scan, automatically append scan results
            started = timestamp(datetime.utcnow())
            results.status = self.module.scan(paths)
            stopped = timestamp(datetime.utcnow())
            results.duration = stopped - started
            # add scan results or append error
            if results.status < 0:
                results.error = self.module.scan_results
            else:
                # as only one result is expected, we simply remove the filename
                # and we return the result got
                results.results = self.module.scan_results.values()[0]
        except Exception as e:
            results.status = -1
            results.error = str(e)
        return results

    @staticmethod
    def file_metadata(filename):
        result = dict()
        if os.path.exists(filename):
            result['mtime'] = os.path.getmtime(filename)
            result['ctime'] = os.path.getctime(filename)
            with open(filename, 'rb') as fd:
                result['sha256'] = hashlib.sha256(fd.read()).hexdigest()
        return result
