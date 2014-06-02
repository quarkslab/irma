#
# Copyright (c) 2013-2014 QuarksLab.
# This file is part of IRMA project.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License in the top-level directory
# of this distribution and at:
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# No part of the project, including this file, may be copied,
# modified, propagated, or distributed except according to the
# terms contained in the LICENSE file.

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
