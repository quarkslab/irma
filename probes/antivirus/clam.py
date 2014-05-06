from celery.utils.log import get_task_logger
from modules.antivirus.clam import Clam
from probes.antivirus.antivirus import AntivirusProbe

log = get_task_logger(__name__)


class ClamProbe(AntivirusProbe):

    ##########################################################################
    # plugin metadata
    ##########################################################################

    _plugin_name = "ClamAV"
    _plugin_version = "0.0.0"
    _plugin_description = "Antivirus plugin for Clam Antivirus"

    ##########################################################################
    # constructor and destructor stuff
    ##########################################################################

    def __init__(self, conf=None, **kwargs):
        # call super classes constructors
        super(ClamProbe, self).__init__(conf, **kwargs)
        self._module = Clam()
