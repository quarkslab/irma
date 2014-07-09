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

import sys
import pprint

from time import mktime
from datetime import datetime
from lib.common.utils import to_unicode


class PluginResult(object):

    def __init__(self, plugin, *args, **kwargs):
        # define plugin metadata
        self._metadata = {
            'plugin': plugin,
            'start_time': None,
            'end_time': None,
            'duration': None,
        }

        # parsed data & result code
        self._data = None
        self._result_code = 0

    @property
    def plugin(self):
        return self.metadata.get('plugin')

    @property
    def start_time(self):
        return self.metadata.get('start_time')

    @start_time.setter
    def start_time(self, value):
        # ignore passed value
        now = datetime.utcnow()
        self.metadata['start_time'] = mktime(now.timetuple()) + \
                                      now.microsecond / 1000000.0

    @property
    def end_time(self):
        return self.metadata.get('end_time')

    @end_time.setter
    def end_time(self, value):
        # ignore passed value
        now = datetime.utcnow()
        self.metadata['end_time'] = mktime(now.timetuple()) + \
                                    now.microsecond / 1000000.0
        self._calculate_duration()

    def _calculate_duration(self):
        start = self.metadata.get('start_time')
        end = self.metadata.get('end_time')
        delta = end - start
        self.metadata['duration'] = delta

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data

    @property
    def result_code(self):
        return self._result_code

    @result_code.setter
    def result_code(self, result_code):
        self._result_code = result_code

    @property
    def metadata(self):
        return self._metadata

    @metadata.setter
    def metadata(self, metadata):
        self._metadata = metadata

    def serialize(self):
        start = self.metadata.get('start_time')
        end = self.metadata.get('end_time')
        result = {
            'metadata': {
                'plugin': self.metadata.get('plugin'),
                'start_time': self.metadata.get('start_time'),
                'end_time': self.metadata.get('end_time'),
                'duration': self.metadata.get('duration'),
                'platform': sys.platform
            },
            'data': self.data,
            'result_code': self.result_code,
        }
        result = to_unicode(result)
        return result

    def __repr__(self):
        return pprint.pformat(self.serialize())
