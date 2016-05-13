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

import logging
from brain.models.sqlobjects import Job
from brain.helpers.sql import session_transaction

log = logging.getLogger(__name__)


def new(scan_id, task_id):
    with session_transaction() as session:
        j = Job(scan_id, task_id)
        j.save(session)
        session.commit()
        log.debug("job %s scan %s",
                  task_id, scan_id)
        return j.task_id
