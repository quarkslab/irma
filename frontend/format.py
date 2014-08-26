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

from lib.plugins import PluginManager
from lib.plugin_result import PluginResult


class IrmaFormatter:

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, class_):
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        manager = PluginManager()
        manager.discover("frontend/formatters", "frontend.formatters")
        self.formatters = manager.get_all_plugins()

    @classmethod
    def format(cls, probe_name, raw_result):
        res = PluginResult(**raw_result)
        try:
            # call formatter until one declares that it can handle it
            for formatter in cls().formatters:
                if formatter.can_handle_results(res):
                    res = formatter.format(res)
                    logging.debug("Using formatter {0} for raw results: {1}"
                                  "".format(formatter.plugin_name, res))
                    break
            # reduce output to hide or to overload the client unnecessarily
            res.pop('platform', None)
            if res.status < 0:
                res.pop('results', None)
            else:
                res.pop('error', None)
        except Exception as e:
            res.pop('results', None)
            res.status = -1
            res.error = e
        return res
