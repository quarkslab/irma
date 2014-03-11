import logging

from lib.common.oopatterns import Plugin
from lib.plugin_result import PluginResult
from probes.processing import Processing

log = logging.getLogger(__name__)

class WebProbe(Plugin, Processing):
    
    ##########################################################################
    # plugin metadata
    ##########################################################################

    _plugin_name = None
    _plugin_version = None
    _plugin_description = None
    _plugin_dependencies = []

    ##########################################################################
    # processing interface
    ##########################################################################

    # TODO: create an object to hold antivirus data instead of a dict
    def run(self, paths):
        # allocate plugin results place-holders
        plugin_results = PluginResult(type(self).plugin_name)
        # query page
        plugin_results.start_time = None
        results = self.scan(paths)
        plugin_results.end_time = None
        # update results
        plugin_results.result_code = results['result_code']
        plugin_results.data = {paths: results}
        # append dependency data
        if type(self).plugin_dependencies:
            for dependency in type(self).plugin_dependencies:
                plugin_results.add_dependency_data(dependency().run())
        return plugin_results.serialize()
