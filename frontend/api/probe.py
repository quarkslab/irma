from bottle import Bottle
from lib.irma.common.utils import IrmaFrontendReturn
import frontend.controllers.braintasks as celery_brain


# ==========
#  File api
# ==========

probe_app = Bottle()


# ===========
#  Probe api
# ===========

@probe_app.get("/list")
def probe_list():
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
