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

import logging
from frontend.models.sqlobjects import File
from frontend.helpers.sessions import session_transaction

log = logging.getLogger(__name__)


# used by tasks.py
def remove_files(max_age_sec):
    with session_transaction() as session:
        nb_deleted = File.remove_old_files(max_age_sec, session)
        log.debug("Max_age_sec: %s Nb_deleted: %s", max_age_sec)
        return nb_deleted
