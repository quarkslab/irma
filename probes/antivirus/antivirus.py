import logging, os, hashlib, datetime

from lib.common.oopatterns import Plugin
from lib.plugin_result import PluginResult
from probes.processing import Processing
from probes.information.system import System

log = logging.getLogger(__name__)

class AntivirusProbe(Plugin, Processing):
    
    ##########################################################################
    # plugin metadata
    ##########################################################################

    _plugin_name = None
    _plugin_version = None
    _plugin_description = None
    _plugin_dependencies = [
        System, # append system information
    ]

    ##########################################################################
    # Helpers
    ##########################################################################

    @staticmethod
    def file_metadata(filename):
        result = dict()
        if os.path.exists(filename):
            result['mtime'] = os.path.getmtime(filename)
            result['ctime'] = os.path.getctime(filename)
            with open(filename, 'rb') as fd:
                result['sha256'] = hashlib.sha256(fd.read()).hexdigest()
        return result

    ##########################################################################
    # processing interface
    ##########################################################################

    # TODO: create an object to hold antivirus data instead of a dict
    def run(self, paths, heuristic=None):
        # allocate plugin results place-holders
        plugin_results = PluginResult(type(self).plugin_name)
        # launch an antivirus scan, automatically append scan results to
        # antivirus.results.
        plugin_results.start_time = None
        plugin_results.result_code = self.scan(paths, heuristic)
        plugin_results.end_time = None
        # allocate memory for data, and fill with data
        plugin_results.data = dict()
        plugin_results.data['name'] = self.name
        plugin_results.data['version'] = self.version
        plugin_results.data['database'] = dict()
        # calculate database metadata
        if self.database:
            for filename in self.database:
                plugin_results.data['database'][filename] = self.file_metadata(filename)
        plugin_results.data['scan_results'] = self.scan_results
        # append dependency data
        if type(self).plugin_dependencies:
            for dependency in type(self).plugin_dependencies:
                plugin_results.add_dependency_data(dependency().run())
        return plugin_results.serialize()
