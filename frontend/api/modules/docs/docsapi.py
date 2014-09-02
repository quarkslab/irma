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
        #self._app.route('/popo/<filename:re(files|probes|scans)>', callback=self._api_declaration)
        self._app.route('/', callback=self._resource_listing)
        self._app.route('/<filename>', callback=self._api_declaration)

    def _resource_listing(self):
        try:
            import yaml
            import json

            with open('docs/api/specs/api-docs.yml') as file:
                data = yaml.load(file)

                bottle.response.content_type = "application/json"
                return json.dumps(data)

        except Exception as e:
            return IrmaFrontendReturn.error(str(e))


    def _api_declaration(self, filename = "files"):
        try:
            import yaml
            import json

            with open('docs/api/specs/' + filename + '.yml') as file:
                data = yaml.load(file)
                data.update(yaml.load(open('docs/api/specs/common.yml')))

                bottle.response.content_type = "application/json"
                return json.dumps(data)

        except Exception as e:
            return IrmaFrontendReturn.error(str(e))
