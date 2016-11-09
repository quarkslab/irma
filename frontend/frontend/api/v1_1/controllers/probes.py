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

import logging
from bottle import response
from frontend.api.v1_1.errors import process_error
import frontend.controllers.braintasks as celery_brain

log = logging.getLogger(__name__)


def list():
    """ get active probe list. This list is used to launch a scan.
    """
    try:
        probelist = celery_brain.probe_list()
        log.debug("probe list: %s", "-".join(probelist))
        response.content_type = "application/json; charset=UTF-8"
        return {
            "total": len(probelist),
            "data": probelist
        }
    except Exception as e:
        log.exception(e)
        process_error(e)
