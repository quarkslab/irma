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

from bottle import response, abort
from sqlalchemy.orm.exc import NoResultFound

from frontend.helpers.schemas import ApiErrorSchema
from lib.irma.common.exceptions import IrmaDatabaseResultNotFound, \
    IrmaDatabaseError, IrmaValueError


api_error_schema = ApiErrorSchema()


# This object aimed to be serialize by an ApiErrorSchema
class ApiError(object):
    http_status_code = 402

    def __init__(self, type, message=None):
        self.type = type
        self.message = message

    def __repr__(self):
        return '<ApiError(type={self.type!r}, message={self.message!r})'.\
            format(self=self)


# Main function design to return a custom API Error
def process_error(error):
    # Default options if error does not match known error
    abort_code = ApiError.http_status_code
    api_error = ApiError('api_error')
    if isinstance(error, ValueError) or isinstance(error, IrmaValueError):
        api_error = ApiError('invalid_request_error', str(error))
    if isinstance(error, NoResultFound) or \
       isinstance(error, IrmaDatabaseResultNotFound):
        abort_code = 404
        api_error = ApiError('invalid_request_error', "Object not Found")
    if isinstance(error, IrmaDatabaseError):
        api_error = ApiError('api_error')
    # Abort raise an exception catch by Bottle Application
    abort(abort_code, api_error)


def define_errors(application):

    # Define a custom function to return Json API error
    @application.error(404)
    @application.error(ApiError.http_status_code)
    def json_api_error(error):
        response.content_type = "application/json; charset=UTF-8"
        return api_error_schema.dumps(error.body).data
