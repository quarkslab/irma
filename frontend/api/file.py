import re
from bottle import Bottle
from lib.irma.common.utils import IrmaFrontendReturn
import frontend.controllers.filectrl as file_ctrl


# ==========
#  File api
# ==========

file_app = Bottle()


# =====================
#  Common param checks
# =====================

def validate_sha256(sha256):
    """ check hashvalue format - should be a sha256 hexdigest"""
    if not re.match(r'^[0-9a-fA-F]{64}$', sha256):
        raise ValueError("Malformed Sha256")


@file_app.route("/exists/<sha256>")
def file_exists(sha256):
    """ lookup file by sha256 and tell if it exists

    :route: /file/exists/<sha256>
    :param sha256 of the file
    :rtype: dict of 'code': int, 'msg': str
        [, optional 'exists':boolean]
    :return:
        on success 'exists' contains a boolean telling if
        file exists or not
        on error 'msg' gives reason message
    """
    try:
        validate_sha256(sha256)
        exists = file_ctrl.exists(sha256)
        return IrmaFrontendReturn.success(exists=exists)
    except Exception as e:
        return IrmaFrontendReturn.error(str(e))


@file_app.route("/result/<sha256>")
def file_result(sha256):
    """ lookup file by sha256

    :route: /file/search/<scanid>
    :param sha256 of the file
    :rtype: dict of 'code': int, 'msg': str
        [, optional 'scan_results': dict of [
            sha256 value: dict of
                'filenames':list of filename,
                'results': dict of [str probename: dict [results of probe]]]]
    :return:
        on success 'scan_results' contains results for file
        on error 'msg' gives reason message
    """
    try:
        validate_sha256(sha256)
        res = file_ctrl.result(sha256)
        return IrmaFrontendReturn.success(scan_results=res)
    # handle all errors/warning as errors
    # file existence should be tested before calling this route
    except Exception as e:
        return IrmaFrontendReturn.error(str(e))


@file_app.route("/infected/<sha256>")
def file_infected(sha256):
    """ lookup file by sha256 and tell if av detect it as
        infected

    :route: /file/suspicious/<sha256>
    :param sha256 of the file
    :rtype: dict of 'code': int, 'msg': str
        [, optional 'infected':boolean, 'nb_detected':int, 'nb_scan':int]
    :return:
        on success 'infected' contains boolean results
        with details in 'nb_detected' and 'nb_scan'
        on error 'msg' gives reason message
    """
    try:
        validate_sha256(sha256)
        return file_ctrl.infected(sha256)
    except Exception as e:
        return IrmaFrontendReturn.error(str(e))
