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

import logging

from api.common.sessions import session_transaction
from api.files.models import File

log = logging.getLogger(__name__)


def remove_files(max_age_sec):
    """
    Delete old files from FS, nullify path value in DB

    :param max_age_sec: limit of file age in seconds
    :return: number of files deleted
    """
    with session_transaction() as session:
        nb_deleted = File.remove_old_files(max_age_sec, session)
        log.debug("Max_age_sec: %s Nb_deleted: %s", max_age_sec, nb_deleted)
        return nb_deleted


def remove_files_size(max_size):
    """
    Delete old files from FS, nullify path value in DB

    :param max_size: limit of space in bytes attributed to the file system
    :return: number of deleted files
    """
    with session_transaction() as session:
        nb_deleted = File.remove_files_max_size(max_size, session)
        log.debug("Max_size: %s Nb_deleted: %s", max_size, nb_deleted)
        return nb_deleted
