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

from modules.antivirus.eset_nod32 import EsetNod32
from probes.antivirus.antivirus import AntivirusProbe

log = logging.getLogger(__name__)


class EsetNod32Probe(AntivirusProbe):

    ##########################################################################
    # plugin metadata
    ##########################################################################

    _plugin_name = "EsetNod32"
    _plugin_version = "0.0.0"
    _plugin_description = ("Antivirus plugin for " +
                           "ESET NOD32 Antivirus " +
                           "Business Edition " +
                           "for Linux Desktop")

    ##########################################################################
    # constructor and destructor stuff
    ##########################################################################

    def __init__(self, conf=None, **kwargs):
        # call super classes constructors
        super(EsetNod32Probe, self).__init__(conf, **kwargs)
        self._module = EsetNod32()
