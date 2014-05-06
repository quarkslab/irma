from celery.utils.log import get_task_logger
from modules.antivirus.symantec import Symantec
from probes.antivirus.antivirus import AntivirusProbe

log = get_task_logger(__name__)


class SymantecProbe(AntivirusProbe):

    ##########################################################################
    # plugin metadata
    ##########################################################################

    _plugin_name = "Symantec"
    _plugin_version = "0.0.0"
    _plugin_description = "Antivirus plugin for Symantec Antivirus"

    ##########################################################################
    # constructor and destructor stuff
    ##########################################################################

    def __init__(self, conf=None, **kwargs):
        # call super classes constructors
        super(SymantecProbe, self).__init__(conf, **kwargs)
        self._module = Symantec()
