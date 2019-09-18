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
import json
from hug.types import one_of, uuid
from falcon.errors import HTTPInvalidParam
from irma.common.utils.utils import decode_utf8

from api.common.middlewares import db

from .helpers import get_file_ext_schemas, new_file_ext
from .models import FileExt, File

log = logging.getLogger("hug")


@hug.get("/{external_id}")
def get(hug_api_version,
        external_id: uuid,
        formatted: one_of(("yes", "no")) = "yes"):
    """ Retrieve a single file_ext result, with details.
    """
    session = db.session
    formatted = False if formatted == 'no' else True
    log.debug("resultid %s formatted %s", external_id, formatted)
    file_ext = FileExt.load_from_ext_id(external_id, session)
    schema = get_file_ext_schemas(file_ext.submitter)
    schema.context = {'formatted': formatted,
                      'api_version': hug_api_version}
    data = schema.dump(file_ext).data
    return data


@hug.post("/", versions=2,
          input_format=hug.input_format.multipart)
def create(request):
    """ Create a file_ext (could be later attached to a scan
        The request should be performed using a POST request method.
        Input format is multipart-form-data with file and a json containing
        at least the submitter type
    """
    log.debug("create file")
    session = db.session

    # request._params is init by Falcon
    # Multipart Middleware giving a dict of part in the form
    form_dict = request._params
    if 'files' not in form_dict:
        raise HTTPInvalidParam("Empty list", "files")
    form_file = form_dict.pop('files')
    if type(form_file) is list:
        raise HTTPInvalidParam("Only one file at a time", "files")

    if 'json' not in form_dict:
        raise HTTPInvalidParam("Missing json parameter", "json")
    payload = json.loads(form_dict['json'])
    submitter = payload.pop('submitter', None)

    # ByteIO object is in file
    data = form_file.file
    filename = decode_utf8(form_file.filename)
    file = File.get_or_create(data, session)
    file_ext = new_file_ext(submitter, file, filename, payload)
    session.add(file_ext)
    session.commit()
    log.debug("filename: %s file_ext: %s created", filename,
              file_ext.external_id)
    schema = get_file_ext_schemas(file_ext.submitter)
    schema.exclude += ("probe_results",)
    return schema.dump(file_ext).data
