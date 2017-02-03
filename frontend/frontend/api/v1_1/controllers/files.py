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
from bottle import response, request

from frontend.api.v1_1.errors import process_error
from frontend.helpers.utils import guess_hash_type
from frontend.models.sqlobjects import FileWeb, File
from frontend.api.v1_1.schemas import FileWebSchema_v1_1, ScanSchema_v1_1, \
    FileSchema_v1_1
from lib.common.utils import decode_utf8
from lib.irma.common.exceptions import IrmaDatabaseResultNotFound


file_web_schema = FileWebSchema_v1_1()
scan_schema = ScanSchema_v1_1()
file_web_schema.context = {'formatted': True}
log = logging.getLogger(__name__)
file_web_schema_lite = FileWebSchema_v1_1(exclude=['probe_results'])
file_web_schema_lite.context = {'formatted': True}

def list(db):
    """ Search a file using query filters (tags + hash or name). Support
        pagination.
    :param all params are sent using query method
    :rtype: dict of 'total': int, 'page': int, 'per_page': int,
        'items': list of file(s) found
    :return:
        on success 'items' contains a list of files found
        on error 'msg' gives reason message
    """
    try:
        name = None
        if 'name' in request.query:
            name = decode_utf8(request.query['name'])

        h_value = request.query.get('hash')

        search_tags = request.query.get('tags')
        if search_tags is not None:
            search_tags = search_tags.split(',')

        log.debug("name %s h_value %s search_tags %s",
                  name, h_value, search_tags)
        if name is not None and h_value is not None:
            raise ValueError("Can't find using both name and hash")

        # Get values from query or default
        offset = request.query.get("offset", default=0)
        offset = int(offset)
        limit = request.query.get("limit", default=25)
        limit = int(limit)

        if name is not None:
            base_query = FileWeb.query_find_by_name(name, search_tags, db)
        elif h_value is not None:
            h_type = guess_hash_type(h_value)

            if h_type is None:
                raise ValueError("Hash not supported")

            base_query = FileWeb.query_find_by_hash(
                h_type, h_value, search_tags, db)
        else:
            # FIXME this is just a temporary way to output
            # all files, need a dedicated
            # file route and controller
            base_query = FileWeb.query_find_by_name("", search_tags, db)

        # TODO: Find a way to move pagination as a BaseQuery like in
        #       flask_sqlalchemy.
        # https://github.com/mitsuhiko/flask-sqlalchemy/blob/master/flask_sqlalchemy/__init__.py#L422
        items = base_query.limit(limit).offset(offset).all()

        if offset == 0 and len(items) < limit:
            total = len(items)
        else:
            total = base_query.count()

        log.debug("Found %s results", total)
        response.content_type = "application/json; charset=UTF-8"
        return {
            'total': total,
            'offset': offset,
            'limit': limit,
            'items': file_web_schema_lite.dump(items, many=True).data,
        }
    except Exception as e:
        log.exception(e)
        process_error(e)


def get(sha256, db):
    """ Detail about one file and all known scans summary where file was
    present (identified by sha256). Support pagination.
    :param all params are sent using query method
    :param if alt parameter is "media", response will contains the binary data
    :rtype: dict of 'total': int, 'page': int, 'per_page': int,
    :return:
        on success fileinfo contains file information
        on success 'items' contains a list of files found
        on error 'msg' gives reason message
    """
    try:
        log.debug("h_value %s", sha256)
        # Check wether its a download attempt or not
        if request.query.alt == "media":
            return _download(sha256, db)

        # Get values from query or default
        offset = request.query.get("offset", default=0)
        offset = int(offset)
        limit = request.query.get("limit", default=25)
        limit = int(limit)

        file = File.load_from_sha256(sha256, db)
        # query all known results not only those with different names
        base_query = FileWeb.query_find_by_hash("sha256", sha256, None, db,
                                                distinct_name=False)

        # TODO: Find a way to move pagination as a BaseQuery like in
        #       flask_sqlalchemy.
        # https://github.com/mitsuhiko/flask-sqlalchemy/blob/master/flask_sqlalchemy/__init__.py#L422
        items = base_query.limit(limit).offset(offset).all()

        if offset == 0 and len(items) < limit:
            total = len(items)
        else:
            total = base_query.count()

        log.debug("offset %d limit %d total %d", offset, limit, total)
        file_web_schema = FileWebSchema_v1_1(exclude=('probe_results',
                                                      'file_infos'))
        fileinfo_schema = FileSchema_v1_1()
        # TODO: allow formatted to be a parameter
        formatted = True
        fileinfo_schema.context = {'formatted': formatted}
        response.content_type = "application/json; charset=UTF-8"
        return {
            'file_infos': fileinfo_schema.dump(file).data,
            'total': total,
            'offset': offset,
            'limit': limit,
            'items': file_web_schema.dump(items, many=True).data,
        }
    except Exception as e:
        log.exception(e)
        process_error(e)


def add_tag(sha256, tagid, db):
    """ Attach a tag to a file.
    """
    try:
        log.debug("h_value %s tagid %s", sha256, tagid)
        fobj = File.load_from_sha256(sha256, db)
        fobj.add_tag(tagid, db)
        db.commit()
    except Exception as e:
        log.exception(e)
        process_error(e)


def remove_tag(sha256, tagid, db):
    """ Remove a tag attached to a file.
    """
    try:
        log.debug("h_value %s tagid %s", sha256, tagid)
        fobj = File.load_from_sha256(sha256, db)
        fobj.remove_tag(tagid, db)
        db.commit()
    except Exception as e:
        log.exception(e)
        process_error(e)


# called by get
def _download(sha256, db):
    """Retrieve a file based on its sha256"""
    log.debug("h_value %s", sha256)
    fobj = File.load_from_sha256(sha256, db)
    # check if file is still present
    if fobj.path is None:
        raise IrmaDatabaseResultNotFound("downloading a removed file")
    # Force download
    ctype = 'application/octet-stream; charset=UTF-8'
    # Suggest Filename to sha256
    cdisposition = "attachment; filename={}".format(sha256)
    response.headers["Content-Type"] = ctype
    response.headers["Content-Disposition"] = cdisposition
    return open(fobj.path).read()
