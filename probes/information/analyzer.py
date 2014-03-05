import logging

from modules.information.analyzer import StaticAnalyzer
from probes.information.information import InformationProbe


log = logging.getLogger(__name__)

class StaticAnalyzerProbe(StaticAnalyzer, InformationProbe):
    
    ##########################################################################
    # plugin metadata
    ##########################################################################

    _plugin_name = "StaticAnalyzer"
    _plugin_version = "0.0.0"
    _plugin_description = "Information plugin to get static information"

    ##########################################################################
    # constructor and destructor stuff
    ##########################################################################

    def __init__(self, *args, **kwargs):
        # call super classes constructors
        super(StaticAnalyzerProbe, self).__init__(*args, **kwargs)
