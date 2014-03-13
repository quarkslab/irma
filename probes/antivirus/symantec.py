import logging

from modules.antivirus.symantec import Symantec
from probes.antivirus.antivirus import AntivirusProbe


log = logging.getLogger(__name__)

class SymantecProbe(AntivirusProbe, Symantec):
    
    ##########################################################################
    # plugin metadata
    ##########################################################################

    _plugin_name = "Symantec"
    _plugin_version = "0.0.0"
    _plugin_description = "Antivirus plugin for Symantec Antivirus"

    ##########################################################################
    # constructor and destructor stuff
    ##########################################################################

    def __init__(self, *args, **kwargs):
        # call super classes constructors
        super(SymantecProbe, self).__init__(*args, **kwargs)
