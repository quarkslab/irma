import logging

from modules.database.nsrl import NSRL
from probes.database.database import DatabaseProbe


log = logging.getLogger(__name__)

class NSRLProbe(NSRL, DatabaseProbe):
    
    ##########################################################################
    # plugin metadata
    ##########################################################################

    _plugin_name = "NSRL"
    _plugin_version = "0.0.0"
    _plugin_description = "Information plugin to query hashes on NRSL database"

    ##########################################################################
    # constructor and destructor stuff
    ##########################################################################

    def __init__(self, conf=None, *args, **kwargs):
        # TODO: move api key in a configuration file
        kwargs['nsrl_os_db'] = conf.get('nsrl_os_db', None) if conf else None
        kwargs['nsrl_mfg_db'] = conf.get('nsrl_mfg_db', None) if conf else None
        kwargs['nsrl_file_db'] = conf.get('nsrl_file_db', None) if conf else None
        kwargs['nsrl_prod_db'] = conf.get('nsrl_prod_db', None) if conf else None
        # call super classes constructors
        super(NSRLProbe, self).__init__(*args, **kwargs)
