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



def get_stats(db):
    """ Get statistics on submitted files using query filters (tags + hash or name).
    :param all params are sent using query method
    :rtype: dict of 'total': int, 'page': int, 'per_page': int,
        'items': list of file(s) found
    :return:
        on success 'items' contains a statistics by avs.
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
        limit = request.query.get("limit", default=0)
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
        items = base_query.all()
        #items = base_query.limit(limit).offset(offset).all()

        files_infos = file_web_schema.dump(items, many=True).data


        stats = []

        # Get scan result for each file
        for i, val in enumerate(files_infos):

            probe_results = val['probe_results']

            for j, res in enumerate(probe_results):

                if res.type == "antivirus":
                    add_stats(stats,res)


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
            'items': stats,
        }
    except Exception as e:
        log.exception(e)
        process_error(e)



def add_stats(stats, result):

    
    for i, val in enumerate(stats):
        
        if val['name'] == result.name:
            # update stats.
            val['total'] += 1
            val['infected'] = val['infected']+1 if result.status == 1 else val['infected']
            val['clean'] = val['clean']+1 if result.status == 0 else val['clean']
            val['errors'] = val['errors']+1 if result.status == -1 else val['errors']
            return 1


    # add new entry in av stats:
    av = {  
        "name":result.name,
        "version": result.version,
        "total": 1,
        "infected": 1 if result.status == 1 else 0 ,
        "clean": 1 if result.status == 0 else 0 ,
        "errors": 1 if result.status == -1 else 0
    }

    stats.append(av)
    
    
    return 0
