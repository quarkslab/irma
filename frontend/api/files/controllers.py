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

import hug
from hug.types import text, number, one_of, comma_separated_list

from api.common.middlewares import db
from api.common.utils import guess_hash_type
from api.files_ext.models import FileExt
from api.files_ext.schemas import FileExtSchema
from api.scans.schemas import ScanSchema
from irma.common.utils.utils import decode_utf8
from irma.common.base.exceptions import IrmaDatabaseResultNotFound
from .models import File
from .schemas import FileSchema

file_ext_schema = FileExtSchema()
scan_schema = ScanSchema()
file_ext_schema.context = {'formatted': True}
log = logging.getLogger(__name__)
file_ext_schema_lite = FileExtSchema(exclude=['probe_results',
                                              'other_results'])
file_ext_schema_lite.context = {'formatted': True}
file_schema = FileSchema()


@hug.get('/')
def list(name: text = None,
         hash: text = None,
         tags: comma_separated_list = None,
         offset: number = 0,
         limit: number = 25):
    """ Search a file using query filters (tags + hash or name). Support
        pagination.
        :param name: lookup name
        :param hash: lookup hash value
        :param tags: lookup tag list
        :param offset: start index in matching results
        :param limit: max number of results
        :rtype: dict of 'total': int, 'page': int, 'per_page': int,
        'items': list of file(s) found
        :return:
        on success 'items' contains a list of files found
        on error 'msg' gives reason message
    """
    session = db.session
    if name is not None:
        name = decode_utf8(name)

    log.debug("name %s h_value %s tags %s",
              name, hash, tags)
    if name is not None and hash is not None:
        raise ValueError("Can't find using both name and hash")

    if name is not None:
        base_query = FileExt.query_find_by_name(name, tags, session)
    elif hash is not None:
        h_type = guess_hash_type(hash)

        if h_type is None:
            raise ValueError("Hash not supported")

        base_query = FileExt.query_find_by_hash(
            h_type, hash, tags, session)
    else:
        # FIXME this is just a temporary way to output
        # all files, need a dedicated
        # file route and controller
        base_query = FileExt.query_find_by_name("", tags, session)

    # TODO: Find a way to move pagination as a BaseQuery like in
    #       flask_sqlalchemy.
    # https://github.com/mitsuhiko/flask-sqlalchemy/blob/master/flask_sqlalchemy/__init__.py#L422
    items = base_query.limit(limit).offset(offset).all()

    if offset == 0 and len(items) < limit:
        total = len(items)
    else:
        total = base_query.count()

    log.debug("Found %s results", total)
    return {
        'total': total,
        'offset': offset,
        'limit': limit,
        'items': file_ext_schema_lite.dump(items, many=True).data,
    }


@hug.get('/{sha256}')
def get(response,
        sha256: text,
        offset: number = 0,
        limit: number = 25):
    """ Detail about one file and all known scans summary where file was
    present (identified by sha256). Support pagination.
    :param sha256: full sha256 value to look for
    :param offset: start index in matching results
    :param limit: max number of results
    :rtype: dict of 'total': int, 'page': int, 'per_page': int,
    :return:
        on success fileinfo contains file information
        on success 'items' contains a list of files found
        on error 'msg' gives reason message
    """
    session = db.session
    log.debug("h_value %s", sha256)

    file = File.load_from_sha256(sha256, session)
    # query all known results not only those with different names
    base_query = FileExt.query_find_by_hash("sha256", sha256, None,
                                            session, distinct_name=False)

    # TODO: Find a way to move pagination as a BaseQuery like in
    #       flask_sqlalchemy.
    # https://github.com/mitsuhiko/flask-sqlalchemy/blob/master/flask_sqlalchemy/__init__.py#L422
    items = base_query.limit(limit).offset(offset).all()

    if offset == 0 and len(items) < limit:
        total = len(items)
    else:
        total = base_query.count()

    log.debug("offset %d limit %d total %d", offset, limit, total)
    file_ext_schema = FileExtSchema(exclude=('probe_results',
                                             'file_infos'))
    fileinfo_schema = FileSchema()
    # TODO: allow formatted to be a parameter
    formatted = True
    fileinfo_schema.context = {'formatted': formatted}
    return {
        'file_infos': fileinfo_schema.dump(file).data,
        'total': total,
        'offset': offset,
        'limit': limit,
        'items': file_ext_schema.dump(items, many=True).data,
    }


@hug.get('/{sha256}/tags/{tagid}/add')
def add_tag(sha256: text, tagid: number):
    """ Attach a tag to a file.
    """
    session = db.session
    log.debug("h_value %s tagid %s", sha256, tagid)
    fobj = File.load_from_sha256(sha256, session)
    fobj.add_tag(tagid, session)
    session.commit()


@hug.get('/{sha256}/tags/{tagid}/remove')
def remove_tag(sha256: text, tagid: number):
    """ Remove a tag attached to a file.
    """
    session = db.session
    log.debug("h_value %s tagid %s", sha256, tagid)
    fobj = File.load_from_sha256(sha256, session)
    fobj.remove_tag(tagid, session)
    session.commit()


# called by get
@hug.get('/{sha256}/download', output=hug.output_format.file)
def download(response, sha256: text,
             filename: text = None):
    """Retrieve a file based on its sha256
    """
    session = db.session
    log.debug("h_value %s", sha256)
    fobj = File.load_from_sha256(sha256, session)
    # check if file is still present
    if fobj.path is None:
        raise IrmaDatabaseResultNotFound("downloading a removed file")
    # Force download
    ctype = 'application/octet-stream; charset=UTF-8'
    # Suggest Filename to sha256
    if filename is None:
        filename = sha256
    cdisposition = "attachment; filename={}".format(filename)
    response.set_header("Content-Type", ctype)
    response.set_header("Content-Disposition", cdisposition)
    return open(fobj.path)
