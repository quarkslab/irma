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

from celery.utils.log import get_task_logger

from modules.antivirus.sophos import Sophos
from probes.antivirus.antivirus import AntivirusProbe

log = get_task_logger(__name__)


class SophosProbe(AntivirusProbe):

    ##########################################################################
    # plugin metadata
    ##########################################################################

    _plugin_name = "Sophos"
    _plugin_version = "0.0.0"
    _plugin_description = ("Antivirus plugin for Sophos Anti-Virus " +
                           "for Unix plugin CLI mode")

    ##########################################################################
    # constructor and destructor stuff
    ##########################################################################

    def __init__(self, conf=None, **kwargs):
        # call super classes constructors
        super(SophosProbe, self).__init__(conf, **kwargs)
        self._module = Sophos()
