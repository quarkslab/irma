import logging

from lib.plugin_result import PluginResult


log = logging.getLogger(__name__)

class Processing(object):

    def run(self, *args, **kwargs):
        raise NotImplementedError
