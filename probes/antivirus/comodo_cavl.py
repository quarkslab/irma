import logging

from modules.antivirus.comodo_cavl import ComodoCAVL
from probes.antivirus.antivirus import AntivirusProbe


log = logging.getLogger(__name__)

class ComodoCAVLProbe(ComodoCAVL, AntivirusProbe):
    
    ##########################################################################
    # plugin metadata
    ##########################################################################

    _plugin_name = "ComodoCAVL"
    _plugin_version = "0.0.0"
    _plugin_description = "Antivirus plugin for Comodo Antivirus for Linux (CAVL)"

    ##########################################################################
    # constructor and destructor stuff
    ##########################################################################

    def __init__(self, *args, **kwargs):
        # call super classes constructors
        super(ComodoCAVLProbe, self).__init__(*args, **kwargs)
