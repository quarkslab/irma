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

import hug
from api.common.errors import HTTPInvalidParam
from .schemas import TagSchema
from api.tags.models import Tag
from api.common.middlewares import db
import logging


log = logging.getLogger()
tag_schema = TagSchema()
tag_schema.context = {'formatted': True}


@hug.get("/")
def list():
    """ Search for all tags in TAG table using query.
    :return:
        on success 'items' contains a list of all tags
        on error 'msg' gives reason message
    """
    session = db.session
    available_tags = Tag.query_find_all(session)

    return {
        'items': tag_schema.dump(available_tags, many=True).data,
    }


@hug.post("/")
def new(text: hug.types.text = None):
    """ Add a new tag, text is passed as query parameter.
    :return:
        on success new tag object is returned
        on error 'msg' gives reason message
    """
    session = db.session

    if not text:
        raise HTTPInvalidParam("Should not be empty", "text")

    # Check if a tag with same tag already exists
    available_tags = Tag.query_find_all(session)
    if text in [t.text for t in available_tags]:
        raise HTTPInvalidParam("Tag '{}' already exists".format(text), "text")

    # create tag if not already present
    tag = Tag(text)
    session.add(tag)
    session.commit()

    # returns new tag
    return tag_schema.dump(tag).data
