import logging

from modules.antivirus.eset_nod32 import EsetNod32
from probes.antivirus.antivirus import AntivirusProbe


log = logging.getLogger(__name__)

class EsetNod32Probe(AntivirusProbe):
    
    ##########################################################################
    # plugin metadata
    ##########################################################################

    _plugin_name = "EsetNod32"
    _plugin_version = "0.0.0"
    _plugin_description = "Antivirus plugin for ESET NOD32 Antivirus Business Edition for Linux Desktop"

    ##########################################################################
    # constructor and destructor stuff
    ##########################################################################

    def __init__(self, conf=None, **kwargs):
        # call super classes constructors
        super(EsetNod32Probe, self).__init__(conf, **kwargs)
        self._module = EsetNod32()
