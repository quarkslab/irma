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

from bottle import Bottle
from frontend.api.modules.webapi import WebApi
from lib.irma.common.utils import IrmaFrontendReturn
import frontend.controllers.braintasks as celery_brain


# ===========
#  Probe api
# ===========

class ProbeApi(WebApi):
    _mountpath = "/probe"
    _app = Bottle()

    def __init__(self):
        self._app.route('/list', callback=self._list)

    def _list(self):
        """ get active probe list
        :route: /probe/list
        :rtype: dict of 'code': int, 'msg': str
            [, optional 'probe_list': list of str]
        :return:
            on success 'probe_list' contains list of probes names
            on error 'msg' gives reason message
        """
        try:
            probelist = celery_brain.probe_list()
            return IrmaFrontendReturn.success(probe_list=probelist)
        except Exception as e:
            return IrmaFrontendReturn.error(str(e))
