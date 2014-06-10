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

import os
from lib.irma.configuration.ini import TemplatedConfiguration

# =====================
#  Probe configuration
# =====================

template_probe_config = {
    'broker_probe': [
        ('host', TemplatedConfiguration.string, None),
        ('port', TemplatedConfiguration.integer, 5672),
        ('vhost', TemplatedConfiguration.string, None),
        ('username', TemplatedConfiguration.string, None),
        ('password', TemplatedConfiguration.string, None)
    ],
    'backend_probe': [
        ('host', TemplatedConfiguration.string, None),
        ('port', TemplatedConfiguration.integer, 6379),
        ('db', TemplatedConfiguration.integer, None),
    ],
    'ftp_brain': [
        ('host', TemplatedConfiguration.string, None),
        ('port', TemplatedConfiguration.integer, 21),
        ('username', TemplatedConfiguration.string, None),
        ('password', TemplatedConfiguration.string, None),
    ],
}

cwd = os.path.abspath(os.path.dirname(__file__))
cfg_file = "{0}/{1}".format(cwd, "probe.ini")
probe_config = TemplatedConfiguration(cfg_file, template_probe_config)
