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

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from irma.common.utils import sql
import config.parser as config


engine = create_engine(config.sqldb.url, echo=config.sql_debug_enabled(),
                       connect_args={"sslmode": config.sqldb.sslmode,
                                     "sslrootcert": config.sqldb.sslrootcert,
                                     "sslcert": config.sqldb.sslcert,
                                     "sslkey": config.sqldb.sslkey})
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False,
                                         bind=engine))


def session_transaction():
    return sql.transaction(db_session)


def session_query():
    return sql.query(db_session)
