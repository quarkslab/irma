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

import hug
from api.common.sessions import db_session


class DatabaseSessionManager:
    def __init__(self):
        self.session = None

    def connect(self):
        self.session = db_session()

    def close(self):
        self.session.flush()
        self.session.close()

    def init_app(self, app):  # pragma: no cover
        @hug.request_middleware(api=app)
        def process_data(request, response):
            self.connect()

        @hug.response_middleware(api=app)
        def process_data(request, response, resource):
            self.close()

        return app


db = DatabaseSessionManager()
