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
import hug

import api.files.controllers as files_routes
import api.probes.controllers as probes_routes
import api.scans.controllers as scans_routes
import api.tags.controllers as tags_routes
import api.files_ext.controllers as files_ext_routes
import api.about.controllers as about_routes
from api.common.middlewares import db, MultipartMiddleware
from api.common.errors import IrmaExceptionHandler
from config.parser import debug_enabled, setup_debug_logger

logger = logging.getLogger(__name__)

if debug_enabled():
    setup_debug_logger(logger)

logger.debug('[Initialization] Starting Hug')

api = hug.API(__name__)
db.init_app(api)
api.http.add_middleware(MultipartMiddleware())
api.http.add_exception_handler(Exception, IrmaExceptionHandler)

api.extend(files_routes, '/files')
api.extend(probes_routes, '/probes')
api.extend(files_ext_routes, '/files_ext')
api.extend(scans_routes, '/scans')
api.extend(tags_routes, '/tags')
api.extend(about_routes, '/about')

# v1.1 legacy
api.extend(files_ext_routes, '/results')
