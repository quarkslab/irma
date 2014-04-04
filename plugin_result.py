import pprint
from time import mktime
from datetime import datetime


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
        self._raw = None
        self._data = None
        self._dependencies_data = None
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
        self.metadata['start_time'] = datetime.utcnow()

    @property
    def end_time(self):
        return self.metadata.get('end_time')

    @end_time.setter
    def end_time(self, value):
        # ignore passed value
        self.metadata['end_time'] = datetime.utcnow()
        self._calculate_duration()

    def _calculate_duration(self):
        if self.metadata.get('end_time') and \
           self.metadata.get('start_time'):
            delta = self.metadata.get('end_time')
            delta -= self.metadata.get('start_time')
        else:
            delta = datetime.timedelta(0)
        self.metadata['duration'] = int(delta.total_seconds())

    def add_dependency_data(self, result):
        if not self._dependencies_data:
            self._dependencies_data = []
        self._dependencies_data.append(result)

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data

    @property
    def raw(self):
        return self._raw

    @raw.setter
    def raw(self, raw):
        self._raw = raw

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
                'start_time': mktime(start.timetuple()),
                'end_time': mktime(end.timetuple()),
                'duration': self.metadata.get('duration')
            },
            'raw': self.raw,
            'data': self.data,
            'result_code': self.result_code,
            'dependencies_data': self._dependencies_data,
        }
        return result

    def __repr__(self):
        return pprint.pformat(self.serialize())
