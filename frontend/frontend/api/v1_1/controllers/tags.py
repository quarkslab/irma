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

from bottle import response, request
from frontend.api.v1_1.errors import process_error
from frontend.api.v1_1.schemas import TagSchema_v1_1
from frontend.models.sqlobjects import File, Tag
import logging


log = logging.getLogger()
tag_schema = TagSchema_v1_1()
tag_schema.context = {'formatted': True}


def list(db):
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


def new(db):
    """ Add a new tag, text is passed as query parameter.
    :return:
        on success new tag object is returned
        on error 'msg' gives reason message
    """
    try:
        # Check if parameter is set
        if 'text' not in request.json:
            raise ValueError("Missing text parameter")
        text = request.json['text']

        # Check if a tag with same tag already exists
        available_tags = Tag.query_find_all(db)
        if text in [t.text for t in available_tags]:
            raise ValueError("Tag already exists")

        # create tag if not already present
        tag = Tag(text)
        db.add(tag)
        db.commit()

        # returns new tag
        response.content_type = "application/json; charset=UTF-8"
        return tag_schema.dumps(tag).data
    except Exception as e:
        process_error(e)
