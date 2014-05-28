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

from lib.plugin_result import PluginResult

log = logging.getLogger(__name__)


class Processing(object):

    def __init__(self, conf=None, **kwargs):
        # store configuration
        self._conf = conf
        self._module = None

    def ready(self):
        result = False
        if self._module:
            result = True
        return result

    def run(self, *args, **kwargs):
        raise NotImplementedError
