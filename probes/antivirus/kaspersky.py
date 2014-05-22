#
# Copyright (c) 2014 QuarksLab.
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

from modules.antivirus.kaspersky import Kaspersky
from probes.antivirus.antivirus import AntivirusProbe

log = logging.getLogger(__name__)


class KasperskyProbe(AntivirusProbe):

    ##########################################################################
    # plugin metadata
    ##########################################################################

    _plugin_name = "Kaspersky"
    _plugin_version = "0.0.0"
    _plugin_description = "Antivirus plugin for Kaspersky Antivirus"

    ##########################################################################
    # constructor and destructor stuff
    ##########################################################################

    def __init__(self, conf=None, **kwargs):
        # call super classes constructors
        super(KasperskyProbe, self).__init__(conf, **kwargs)
        self._module = Kaspersky()
