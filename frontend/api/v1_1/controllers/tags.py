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

from bottle import response
from frontend.api.v1_1.errors import process_error
from frontend.api.v1_1.schemas import TagSchema_v1_1
from frontend.models.sqlobjects import File, Tag
import logging


log = logging.getLogger()
tag_schema = TagSchema_v1_1()
tag_schema.context = {'formatted': True}


def list_available_tags(db):
    """ Search for all tags in TAG table using query.
    :return:
        on success 'items' contains a list of all tags
        on error 'msg' gives reason message
    """
    try:
        available_tags = Tag.query_find_all(db)

        response.content_type = "application/json; charset=UTF-8"
        return {
            'items': tag_schema.dump(available_tags, many=True).data,
        }
    except Exception as e:
        process_error(e)
