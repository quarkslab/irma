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

from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

import config.parser as config
from lib.irma.common.exceptions import IrmaDatabaseError

db_url = config.get_sql_url()
engine = create_engine(db_url, echo=config.sql_debug_enabled())
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False,
                                         bind=engine))


@contextmanager
def session_transaction():
    """Provide a transactional scope around a series of operations."""
    try:
        yield db_session
        db_session.commit()
    except IrmaDatabaseError:
        db_session.rollback()
        raise
    finally:
        db_session.close()


@contextmanager
def session_query():
    """Provide a transactional scope around a series of operations."""
    try:
        yield db_session
    except IrmaDatabaseError:
        raise
