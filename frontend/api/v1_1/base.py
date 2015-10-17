#
# Copyright (c) 2013-2015 QuarksLab.
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
from bottle.ext import sqlalchemy
from frontend.helpers.sql import engine
from frontend.models.sqlobjects import Base

from frontend.api.v1_1.routes import define_routes
from frontend.api.v1_1.errors import define_errors


"""
    IRMA FRONTEND WEB API
    defines all accessible route accessed via uwsgi..
"""
# main bottle app
application = Bottle()

plugin = sqlalchemy.Plugin(
    # SQLAlchemy engine created with create_engine function.
    engine,
    # SQLAlchemy metadata, required only if create=True.
    Base.metadata,
    # Keyword used to inject session database
    # in a route (default 'db').
    keyword='db',
    # If it is true, execute `metadata.create_all(engine)`
    # when plugin is applied (default False).
    create=True,
    # If it is true, plugin commit changes after route
    # is executed (default True).
    commit=False,
    # If it is true and keyword is not defined,
    # plugin uses **kwargs argument to inject session database (default False).
    use_kwargs=False
)
application.install(plugin)

define_routes(application)
define_errors(application)
