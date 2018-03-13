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

import api.tasks.braintasks as celery_brain

log = logging.getLogger(__name__)


@hug.get('/')
# TODO response with probe objects in v2
def list():
    """get active probe list. This list is used to launch a scan."""
    probelist = celery_brain.probe_list()
    log.debug("probe list: %s", "-".join(probelist))
    return {
        "total": len(probelist),
        "data": sorted(probelist)
    }
