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

from brain.models.sqlobjects import User
from brain.helpers.sql import session_query, session_transaction


def get_userid(rmqvhost):
    with session_query() as session:
        user = User.get_by_rmqvhost(rmqvhost, session)
        return user.id


def get_quota(user_id):
    with session_query() as session:
        user = User.load(user_id, session)
        quota = user.quota
        remaining = None
        if quota is not None:
            remaining = user.remaining_quota(session)
        return (remaining, quota)


def get_ftpuser(user_id):
    with session_query() as session:
        user = User.load(user_id, session)
        return user.ftpuser
