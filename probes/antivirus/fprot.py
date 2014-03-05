import logging

from modules.antivirus.fprot import FProt
from probes.antivirus.antivirus import AntivirusProbe


log = logging.getLogger(__name__)

class FProtProbe(FProt, AntivirusProbe):
    
    ##########################################################################
    # plugin metadata
    ##########################################################################

    _plugin_name = "FProt"
    _plugin_version = "0.0.0"
    _plugin_description = "Antivirus plugin for F-Prot"

    ##########################################################################
    # constructor and destructor stuff
    ##########################################################################

    def __init__(self, *args, **kwargs):
        # call super classes constructors
        super(FProtProbe, self).__init__(*args, **kwargs)
