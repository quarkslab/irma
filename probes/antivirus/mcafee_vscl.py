import logging

from modules.antivirus.mcafee_vscl import McAfeeVSCL
from probes.antivirus.antivirus import AntivirusProbe


log = logging.getLogger(__name__)

class McAfeeVSCLProbe(McAfeeVSCL, AntivirusProbe):
    
    ##########################################################################
    # plugin metadata
    ##########################################################################

    _plugin_name = "McAfeeVSCL"
    _plugin_version = "0.0.0"
    _plugin_description = "Antivirus plugin for McAfee VirusScan Command Line (VSCL) scanner"

    ##########################################################################
    # constructor and destructor stuff
    ##########################################################################

    def __init__(self, *args, **kwargs):
        # call super classes constructors
        super(McAfeeVSCLProbe, self).__init__(*args, **kwargs)
