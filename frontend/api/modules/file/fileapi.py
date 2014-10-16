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

import re
from bottle import Bottle, request
from frontend.api.modules.webapi import WebApi
from lib.irma.common.utils import IrmaFrontendReturn
from lib.irma.common.exceptions import IrmaValueError
from frontend.helpers.serializers import FileWebSerializer
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
        self._app.route('/exists/<sha256>',
                        callback=self._exists)
        self._app.route('/result/<sha256>',
                        callback=self._result)
        self._app.route('/infected/<sha256>',
                        callback=self._infected)
        self._app.route('/findByHash/<hash_val>',
                        callback=self._find_by_hash)
        self._app.route('/findByName/<name:path>',
                        callback=self._find_by_name)
        self._app.route('/search',
                       callback=self._search)

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
        :param formatted boolean to get formatted result or not
               (default to True)
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
            formatted = True
            if 'formatted' in request.params:
                if request.params['formatted'].lower() == 'false':
                    formatted = False
            res = file_ctrl.get_results(sha256, formatted)
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

    def _find_by_hash(self, hash_val):
        """ lookup file by hash and returns sha256
        :route: /findByHash/<hash_val:path>
        :param hash_val of the file (sha1, sha256, md5 are supported)
        :rtype: dict of 'code': int, 'msg': str
            [, optional 'found': dict of items]
        :return:
            on success 'found' contains dict of files found
            on error 'msg' gives reason message
        """
        try:
            hash_type = None
            try:
                validate_sha256(hash_val)
                hash_type = "sha256"
            except ValueError:
                pass
            try:
                validate_sha1(hash_val)
                hash_type = "sha1"
            except ValueError:
                pass
            try:
                validate_md5(hash_val)
                hash_type = "md5"
            except ValueError:
                pass
            if hash_type is None:
                return IrmaFrontendReturn.error("hash not supported")
            # handle optional bool parameters
            desc = False
            if 'desc' in request.params:
                if request.params['desc'].lower() == 'true':
                    desc = True
            # handle optional parameters
            page = request.params.get('page', None)
            page_size = request.params.get('page_size', None)
            order_by = request.params.get('order_by', None)
            # handle list parameters
            fields = request.params.get('fields', None)
            if fields is not None:
                fields = fields.split(",")
            list_items = file_ctrl.find_by_hash(hash_val, hash_type,
                                                page, page_size, order_by,
                                                fields, desc)
            if len(list_items) != 0:
                return IrmaFrontendReturn.success(found=list_items)
            else:
                return IrmaFrontendReturn.error("name not found")
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
            # handle optional bool parameters
            strict = False
            if 'strict' in request.params:
                if request.params['strict'].lower() == 'true':
                    strict = True
            desc = False
            if 'desc' in request.params:
                if request.params['desc'].lower() == 'true':
                    desc = True
            # handle optional parameters
            page = request.params.get('page', None)
            page_size = request.params.get('page_size', None)
            order_by = request.params.get('order_by', None)
            # handle list parameters
            fields = request.params.get('fields', None)
            if fields is not None:
                fields = fields.split(",")
            list_items = file_ctrl.find_by_name(name, strict,
                                                page, page_size, order_by,
                                                fields, desc)
            if len(list_items) != 0:
                return IrmaFrontendReturn.success(found=list_items)
            else:
                return IrmaFrontendReturn.error("name not found")
        except Exception as e:
            return IrmaFrontendReturn.error(str(e))


    def _search(self):
        """ Search a file using query filters
        """
        try:
            name = request.query.name or None
            strict = True if request.query.strict.lower() == 'true' else False
            page = int(request.query.page) if request.query.page else 1
            per_page = int(request.query.per_page) if request.query.per_page else 25

            if name is not None:
                base_query = file_ctrl.query_find_by_name(name, strict)
            else:
                raise IrmaValueError("Cannot find name in query attributes")

            # TODO: Find a way to move pagination as a BaseQuery like in flask_sqlalchemy
            # https://github.com/mitsuhiko/flask-sqlalchemy/blob/master/flask_sqlalchemy/__init__.py#L422
            if page < 1:
                raise IrmaValueError("page attribute cannot be < 1")
            items = base_query.limit(per_page).offset((page - 1) * per_page).all()

            if page == 1 and len(items) < per_page:
                total = len(items)
            else:
                total = base_query.count()

            return {
                'total': total,
                'per_page': per_page,
                'page': page,
                'items': FileWebSerializer(items, many=True).data,
            }
        except Exception as e:
            return IrmaFrontendReturn.error(str(e))
