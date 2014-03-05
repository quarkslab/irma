import logging

from modules.antivirus.clam import Clam
from probes.antivirus.antivirus import AntivirusProbe


log = logging.getLogger(__name__)

class ClamProbe(Clam, AntivirusProbe):
    
    ##########################################################################
    # plugin metadata
    ##########################################################################

    _plugin_name = "ClamAV"
    _plugin_version = "0.0.0"
    _plugin_description = "Antivirus plugin for Clam Antivirus"

    ##########################################################################
    # constructor and destructor stuff
    ##########################################################################

    def __init__(self, *args, **kwargs):
        # call super classes constructors
        super(ClamProbe, self).__init__(*args, **kwargs)
