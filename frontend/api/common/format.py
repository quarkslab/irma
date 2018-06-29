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

import logging

from irma.common.plugins.manager import PluginManager
from irma.common.plugin_result import PluginResult

log = logging.getLogger(__name__)


class IrmaFormatter:

    def __init__(self):
        manager = PluginManager()
        manager.discover("api/common/formatters",
                         "api.common.formatters")
        # TODO add plugin type to distinguish between api/formatter plugin
        all_plugins = manager.get_all_plugins()
        self.formatters = [x for x in all_plugins
                           if not x.plugin_category == "api"]

    @classmethod
    def format(cls, probe_name, raw_result):
        res = PluginResult(**raw_result)
        try:
            # call formatter until one declares that it can handle it
            for formatter in cls().formatters:
                if formatter.can_handle_results(res):
                    res = formatter.format(res)
                    log.debug("using formatter {0} for raw results: {1}"
                              "".format(formatter.plugin_name, res))
                    break
            # reduce output to hide or to overload the client unnecessarily
            res.pop('platform', None)
            if res.status < 0:
                res.pop('results', None)
            else:
                res.pop('error', None)
            duration = res.pop('duration', None)
            if duration is not None:
                # Round duration to 2 decimals
                res['duration'] = round(duration, 2)
        except Exception as e:
            res.pop('results', None)
            res.status = -1
            res.error = e
        return res
