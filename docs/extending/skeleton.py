#
# Copyright (c) 2013-2018 Quarkslab.
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

# Choose the class you need to inherit from
from modules.antivirus.base import AntivirusUnix, AntivirusWindows

log = logging.getLogger(__name__)

# Inhererit from AntivirusUnix or AntivirusWindows according to your plateform
class Skeleton(Antivirus):
    name = "Skeleton for Antivirus"

    # ==================================
    #  Constructor and destructor stuff
    # ==================================

    def __init__(self, *args, **kwargs):
        # class super class constructor
        super().__init__(*args, **kwargs)

        # do your initialization stuff
