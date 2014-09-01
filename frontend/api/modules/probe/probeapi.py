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
