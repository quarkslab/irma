#
# Copyright (c) 2013-2016 Quarkslab.
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

import config.parser as config
from sqlalchemy import create_engine


def generate_url(dbms, dialect, username, passwd, host, dbname):
    if dialect:
        dbms = "{0}+{1}".format(dbms, dialect)
    host_and_id = ''
    if host and username:
        if passwd:
            host_and_id = "{0}:{1}@{2}".format(username, passwd, host)
        else:
            host_and_id = "{0}@{1}".format(username, host)
    return "{0}://{1}/{2}".format(dbms, host_and_id, dbname)


# Retrieve database informations
uri_params = config.get_sql_db_uri_params()
url = generate_url(uri_params[0], uri_params[1], uri_params[2], uri_params[3],
                   uri_params[4], uri_params[5])

engine = create_engine(url, echo=config.sql_debug_enabled())
