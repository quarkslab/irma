import logging

from modules.web.virustotal import VirusTotal
from probes.web.web import WebProbe

log = logging.getLogger(__name__)


class VirusTotalProbe(WebProbe):

    ##########################################################################
    # plugin metadata
    ##########################################################################

    _plugin_name = "VirusTotal"
    _plugin_version = "0.0.0"
    _plugin_description = "Web plugin for Virus Total"

    ##########################################################################
    # constructor and destructor stuff
    ##########################################################################

    def __init__(self, conf=None, *args, **kwargs):
        # call super classes constructors
        super(VirusTotalProbe, self).__init__(*args, **kwargs)
        api_key = conf.get('api_key', None) if conf else None
        try:
            self._module = VirusTotal(api_key)
        except Exception as e:
            log.exception(e)
