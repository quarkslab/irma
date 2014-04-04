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
