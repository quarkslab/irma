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

import sys


# TODO: Replace PluginResult by a class that perform type checking
class PluginResult(dict):
    """
    The following describes the minimal format for PluginResult

    {
        'name'        : str() with the name of the probe
        'type'        : str() with the category of the probe
        'version'     : str() with the version of the probe
        'platform'    : str() with the platform on which the probe is executed

        'duration'    : duration in milliseconds
        'status'      : return code (< 0 is error, 0 > is context specific)
        'error'       : None if no error (state > 0) else str() with the error
        'results'     : Probe results

        [ ... followed by plugin specific data ... ]
    }

    """

    def __getattr__(self, key):
        return self.get(key, None)
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __init__(self, **kwargs):
        # probe identification data
        self.name = kwargs.pop('name', None)
        self.type = kwargs.pop('type', None)
        self.version = kwargs.pop('version', None)
        self.platform = kwargs.pop('platform', sys.platform)

        # probe execution data
        self.duration = kwargs.pop('duration', None)
        self.status = kwargs.pop('status', -1)
        self.error = kwargs.pop('error', None)
        self.results = kwargs.pop('results', None)

        # get remaining values form kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)
