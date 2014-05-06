from celery.utils.log import get_task_logger
from modules.antivirus.fprot import FProt
from probes.antivirus.antivirus import AntivirusProbe

log = get_task_logger(__name__)


class FProtProbe(AntivirusProbe):

    ##########################################################################
    # plugin metadata
    ##########################################################################

    _plugin_name = "FProt"
    _plugin_version = "0.0.0"
    _plugin_description = "Antivirus plugin for F-Prot"

    ##########################################################################
    # constructor and destructor stuff
    ##########################################################################

    def __init__(self, conf=None, **kwargs):
        # call super classes constructors
        super(FProtProbe, self).__init__(conf, **kwargs)
        self._module = FProt()
