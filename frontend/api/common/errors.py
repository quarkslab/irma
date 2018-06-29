#
# Copyright (c) 2013-2018 Quarkslab.
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

import sys
import logging
from hug import HTTPInternalServerError, HTTPInvalidParam, HTTPError
from sqlalchemy.orm.exc import NoResultFound
from falcon import HTTP_404, HTTP_402

from irma.common.base.exceptions import IrmaDatabaseResultNotFound, \
    IrmaDatabaseError, IrmaValueError

log = logging.getLogger(__name__)


class IrmaExceptionHandler:
    exclude = type(None)

    def __init__(self, request, response, exception, **kwargs):
        self.request = request
        self.response = response
        self.exception = exception
        self.process_error(exception)

    # Main function design to return a custom API Error
    @staticmethod
    def process_error(error):
        log.exception("Exception occured: %s", error)
        # Default options if error does not match known error
        if isinstance(error, (ValueError,
                              IrmaValueError)):
            raise HTTPInvalidParam('value_error', str(error))
        elif isinstance(error, (NoResultFound,
                                IrmaDatabaseResultNotFound)):
            raise HTTPError(HTTP_404, title="NoResultFound",
                            description="Result not found")
        elif isinstance(error, IrmaDatabaseError):
            raise HTTPInternalServerError('database_error', "Database error")
        else:
            raise error
