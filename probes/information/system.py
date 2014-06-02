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

import platform
from probes.processing import Processing


class System(Processing):

    def run(self, *args, **kwargs):
        results = dict()
        results = {
            'architecture': platform.machine(),
            'system': platform.system(),
            'version': platform.version(),
            'release': platform.release(),
            'description': None
        }
        # add specific results
        system = results['system']
        if system == 'Linux':
            results['description'] = str(platform.linux_distribution())
        elif system == 'Windows':
            results['description'] = str(platform.win32_ver())
        elif system == 'Darwin':
            results['description'] = str(platform.mac_ver())
        return results
