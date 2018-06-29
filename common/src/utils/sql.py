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
from ..base.exceptions import IrmaDatabaseError

import logging
log = logging.getLogger(__name__)


@contextmanager
def transaction(session):
    """Provide a transactional scope around a series of operations."""
    # TODO: when used with 'with', session is not commited and usage of vars
    #       such as object.id could not be initialized (None)
    try:
        yield session
        session.commit()
    except IrmaDatabaseError:
        log.warning("Transaction failed, rolling back")
        session.rollback()
        raise
    finally:
        session.close()


@contextmanager
def query(session):
    """Provide a transactional scope around a series of operations."""
    try:
        yield session
    except IrmaDatabaseError:
        raise
