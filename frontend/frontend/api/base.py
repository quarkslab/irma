#
# Copyright (c) 2013-2016 Quarkslab.
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

import sys
import logging
from bottle import Bottle
from frontend.api.v1.base import application as app_v1
from frontend.api.v1_1.base import application as app_v1_1
from config.parser import debug_enabled, setup_debug_logger


application = Bottle()
application.mount('/v1', app_v1)
application.mount('/v1.1', app_v1_1)


if debug_enabled():
    setup_debug_logger(logging.getLogger(__name__))
