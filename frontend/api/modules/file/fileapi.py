import re
from bottle import Bottle
from frontend.api.modules.webapi import WebApi
from lib.irma.common.utils import IrmaFrontendReturn
import frontend.controllers.filectrl as file_ctrl


# =====================
#  Common param checks
# =====================

def validate_sha256(sha256):
    """ check hashvalue format - should be a sha256 hexdigest"""
    if not re.match(r'^[0-9a-fA-F]{64}$', sha256):
        raise ValueError("Malformed Sha256")


def validate_sha1(sha1):
    """ check hashvalue format - should be a sha1 hexdigest"""
    if not re.match(r'^[0-9a-fA-F]{40}$', sha1):
        raise ValueError("Malformed Sha1")


def validate_md5(md5):
    """ check hashvalue format - should be a md5 hexdigest"""
    if not re.match(r'^[0-9a-fA-F]{32}$', md5):
        raise ValueError("Malformed md5")


# ==========
#  File api
# ==========

class FileApi(WebApi):
    _mountpath = "/file"
    _app = Bottle()

    def __init__(self):
        self._app.route('/exists/<sha256>', callback=self._exists)
        self._app.route('/result/<sha256>', callback=self._result)
        self._app.route('/infected/<sha256>', callback=self._infected)
        self._app.route('/findByHash/<hashvalue>', callback=self._find_by_hash)
        self._app.route('/findByName/<name:path>', callback=self._find_by_name)

    def _exists(self, sha256):
        """ lookup file by sha256 and tell if it exists
        :route: /exists/<sha256>
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
            exists = (file_ctrl.init_by_sha256(sha256) is not None)
            return IrmaFrontendReturn.success(exists=exists)
        except Exception as e:
            return IrmaFrontendReturn.error(str(e))

    def _result(self, sha256):
        """ lookup file by sha256
        :route: /file/search/<scanid>
        :param sha256 of the file
        :rtype: dict of 'code': int, 'msg': str
            [, optional 'scan_results': dict of [
                sha256 value: dict of
                    'filenames':list of filename,
                    'results': dict of [str probename: 
                                        dict [results of probe]]]]
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

    def _infected(self, sha256):
        """ lookup file by sha256 and tell if av detect it as
            infected
        :route: /suspicious/<sha256>
        :param sha256 of the file
        :rtype: dict of 'code': int, 'msg': str
            [, optional 'infected':boolean, 'nb_detected':int, 
            'nb_scan':int]
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

    def _find_by_hash(self, hashvalue):
        """ lookup file by hash and returns sha256
        :route: /findByHash/<hashvalue>
        :param hashvalue of the file (sha1, sha256, md5 are supported)
        :rtype: dict of 'code': int, 'msg': str
            [, optional 'found': list of (one) sha256 of file found]
        :return:
            on success 'found' contains sha256 of files found
            on error 'msg' gives reason message
        """
        try:
            try:
                validate_sha256(hashvalue)
                if file_ctrl.init_by_sha256(hashvalue) is not None:
                    return IrmaFrontendReturn.success(found=[hashvalue])
                else:
                    return IrmaFrontendReturn.error("hash not found")
            except ValueError:
                pass
            try:
                validate_sha1(hashvalue)
                sha256 = file_ctrl.init_by_sha1(hashvalue)
                if sha256 is not None:
                    return IrmaFrontendReturn.success(found=[sha256])
                else:
                    return IrmaFrontendReturn.error("hash not found")
            except ValueError:
                pass
            try:
                validate_md5(hashvalue)
                sha256 = file_ctrl.init_by_md5(hashvalue)
                if sha256 is not None:
                    return IrmaFrontendReturn.success(found=[sha256])
                else:
                    return IrmaFrontendReturn.error("hash not found")
            except ValueError:
                pass
            return IrmaFrontendReturn.error("hash not supported")
        except Exception as e:
            return IrmaFrontendReturn.error(str(e))

    def _find_by_name(self, name):
        """ lookup file by name
        :route: /findByName/<name:path>
        :param name of the file (partial supported)
        :rtype: dict of 'code': int, 'msg': str
            [, optional 'found': list of sha256 of file(s) found]
        :return:
            on success 'found' contains sha256 of files found
            on error 'msg' gives reason message
        """
        try:
            list_sha256 = file_ctrl.find_by_name(name)
            if len(list_sha256) != 0:
                return IrmaFrontendReturn.success(found=list_sha256)
            else:
                return IrmaFrontendReturn.error("name not found")
        except Exception as e:
            return IrmaFrontendReturn.error(str(e))
