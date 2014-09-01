from bottle import Bottle
from frontend.api.scan import scan_app
from frontend.api.file import file_app
from frontend.api.probe import probe_app
from lib.irma.common.utils import IrmaFrontendReturn


"""
    IRMA FRONTEND WEB API
    defines all accessible route accessed via uwsgi..
"""

application = Bottle()
application.mount('/scan', scan_app)
application.mount('/file', file_app)
application.mount('/probe', probe_app)


# =============
#  Server root
# =============

@application.route("/ping")
def svr_index():
    """ hello world

    :route: /
    :rtype: dict of 'code': int, 'msg': str
    :return: success
    """
    return IrmaFrontendReturn.success()
