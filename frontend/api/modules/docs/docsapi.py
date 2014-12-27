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

import bottle
import yaml
import json

from bottle import Bottle
from frontend.api.modules.webapi import WebApi
from lib.irma.common.utils import IrmaFrontendReturn


docs_app = Bottle()


# ==========
#  Docs api
# ==========

class DocsApi(WebApi):
    _mountpath = "/docs"
    _app = Bottle()

    def __init__(self):
        self._app.route('/', callback=self._resource_listing)
        self._app.route('/<filename>', callback=self._api_declaration)
        self._base = 'frontend/api/modules/docs/specs'

    def _resource_listing(self):
        try:
            with open('{path}/api-docs.yml'.format(path=self._base)) as file:
                data = yaml.load(file)
            bottle.response.content_type = "application/json"
            return json.dumps(data)
        except Exception as e:
            return IrmaFrontendReturn.error(str(e))

    def _api_declaration(self, filename="files"):
        try:
            with open('{path}/{filename}.yml'
                      ''.format(path=self._base, filename=filename)) as file:
                data = yaml.load(file)
            with open('{path}/common.yml'.format(path=self._base)) as file:
                data.update(yaml.load(file))
            bottle.response.content_type = "application/json"
            return json.dumps(data)
        except Exception as e:
            return IrmaFrontendReturn.error(str(e))
