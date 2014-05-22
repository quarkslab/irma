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

from modules.information.analyzer import StaticAnalyzer
from probes.information.information import InformationProbe

log = logging.getLogger(__name__)


class StaticAnalyzerProbe(InformationProbe):

    ##########################################################################
    # plugin metadata
    ##########################################################################

    _plugin_name = "StaticAnalyzer"
    _plugin_version = "0.0.0"
    _plugin_description = "Information plugin to get static information"

    ##########################################################################
    # constructor and destructor stuff
    ##########################################################################

    def __init__(self, conf=None, **kwargs):
        # call super classes constructors
        super(StaticAnalyzerProbe, self).__init__(conf, **kwargs)
        try:
            self._module = StaticAnalyzer()
        except Exception as e:
            log.exception(e)
