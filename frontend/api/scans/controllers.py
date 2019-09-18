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
import ntpath

import hug
from hug.types import number, smart_boolean, uuid, comma_separated_list, text
from falcon.errors import HTTPInvalidParam, HTTPUnauthorized

import api.scans.services as scan_ctrl
import api.probes.services as probe_ctrl
import api.files_ext.controllers as files_ctrl
import api.tasks.frontendtasks as celery_frontend
from api.common.middlewares import db
from api.files.models import File
from api.files_ext.models import FileExt, FileWeb, FileCli
from api.files_ext.schemas import FileExtSchema
from irma.common.utils import compat
from irma.common.base.exceptions import IrmaDatabaseResultNotFound
from irma.common.utils.utils import decode_utf8
from irma.common.base.utils import IrmaScanStatus
from .models import Scan
from .schemas import ScanSchema

import api.files_ext.controllers

scan_schema = ScanSchema()
log = logging.getLogger(__name__)


@hug.get("/")
def list(status: text = None,
         offset: number = 0,
         limit: number = 5):
    """ Get a list of all scans which have been launched.
    """
    session = db.session
    log.debug("offset %s limit %s", offset, limit)
    base_query = session.query(Scan)
    # Lookup status code from status label
    status_code = None
    if status is not None:
        for (k, v) in IrmaScanStatus.label.items():
            if v == status:
                status_code = k
                break
        if status_code is None:
            raise HTTPInvalidParam("unknown value", "status")
        else:
            base_query = base_query.filter(Scan.status == status_code)

    items = base_query.limit(limit).offset(offset).all()

    if offset == 0 and len(items) < limit:
        total = len(items)
    else:
        total = base_query.count()

    log.debug("found %s scans", total)
    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "data": scan_schema.dump(items, many=True).data,
    }


# deprecated in v2+
@hug.post("/", versions=1)
def new(request):
    """ Create a new scan.
        The request should be performed using a POST request method.
    """
    session = db.session
    ip = request.remote_addr
    scan = Scan(compat.timestamp(), ip)
    session.add(scan)

    scan.set_status(IrmaScanStatus.empty)
    session.commit()
    log.debug("scan %s: created", scan.external_id)
    return scan_schema.dump(scan).data


@hug.get("/{scan_id}")
def get(scan_id: uuid):
    """ Retrieve information for a specific scan
    """
    log.debug("scan %s: retrieved", scan_id)
    session = db.session
    scan = Scan.load_from_ext_id(scan_id, session)

    return scan_schema.dump(scan).data


@hug.format.content_type('text/csv; charset=utf-8')
def report_as_csv(scan, request=None, response=None, hug_api_version=2):
    response.append_header('Content-Disposition',
                           ('attachment; filename="Scan report - %s.csv"' %
                            scan.external_id))
    # Using stream is useful when the report generated contains a lot of files
    response.stream = scan_ctrl.generate_csv_report_as_stream(scan)


# For the moment the report is generated in csv format.
# For the future, if you want to generate it depending on the MIME type return
# by the Content-Type header, you can use this:
# @hug.get('/{scan_id}/report', output=hug.output_format.on_content_type(
#     {'text/csv': report_as_csv,
#     'text/plain': report_as_plain}
# ))
@hug.get('/{scan_id}/report', output=report_as_csv)
def get_report(request, response, scan_id: uuid):
    """
    Retrieve the scan report as a csv file
    """
    scan = Scan.load_from_ext_id(scan_id, db.session)

    if scan.finished():
        return scan

    raise HTTPUnauthorized('Scan is not finished.')


@hug.post("/{scan_id}/launch", versions=1)
def launch_v1(scan_id: uuid,
              probes: comma_separated_list = None,
              force: smart_boolean = False,
              mimetype_filtering: smart_boolean = True,
              resubmit_files: smart_boolean = True,
              ):
    """ Launch a scan.
        The request should be performed using a POST request method.
    """
    session = db.session
    scan = Scan.load_from_ext_id(scan_id, session)

    # handle scan parameter
    # cached results: "force" (default: False)
    scan.force = force

    # use mimetype for probelist: "mimetype_filtering" (default: True)
    scan.mimetype_filtering = mimetype_filtering

    # rescan file outputted from probes "resubmit_files" (default: True)
    scan.resubmit_files = resubmit_files
    session.commit()

    msg = "scan %s: Force %s MimeF %s"
    msg += "Resub %s Probes %s"
    log.debug(msg, scan_id, scan.force, scan.mimetype_filtering,
              scan.resubmit_files, probes)
    probelist = probe_ctrl.check_probe(probes)
    log.info("scan %s: probes used: %s", scan_id, probelist)
    scan.set_probelist(probelist)
    session.commit()
    # launch_asynchronous scan via frontend task
    celery_frontend.scan_launch(str(scan_id))

    return scan_schema.dump(scan).data


@hug.post("/", versions=2)
def launch_v2(request, body):
    """ Launch a scan.
        The request should be performed using a POST request method.
        The input json format is the following:
        {
            files: [fileext1, fileext2...]
            options:
               probes: list of probes or None for all available,
               force: boolean (default False),
               mimetype_filtering: boolean (default True),
               resubmit_files: boolean (default True),
        }
    """
    scan_params = body
    if not scan_params:
        raise HTTPInvalidParam("Missing json parameters", "body")
    files_list = body.get('files', None)

    if files_list is None or len(files_list) == 0:
        raise HTTPInvalidParam("Missing values", "files")

    # Set default values
    force = True
    mimetype_filtering = True
    resubmit_files = True
    probes = None
    # override with given values if set
    scan_options = body.get("options", None)
    if scan_options is not None:
        force = scan_options.get("force", force)
        if type(force) is not bool:
            raise HTTPInvalidParam("Should be boolean", "force")
        mimetype_filtering = scan_options.get("mimetype_filtering",
                                              mimetype_filtering)
        if type(mimetype_filtering) is not bool:
            raise HTTPInvalidParam("Should be boolean",
                                   "mimetype_filtering")
        resubmit_files = scan_options.get("resubmit_files", resubmit_files)
        if type(resubmit_files) is not bool:
            raise HTTPInvalidParam("Should be boolean",
                                   "resubmit_files")
        probes = scan_options.get("probes", probes)

    session = db.session
    ip = request.remote_addr

    files_ext = []
    for fe_id in files_list:
        try:
            file_ext = FileExt.load_from_ext_id(fe_id, session)
        except IrmaDatabaseResultNotFound:
            raise HTTPInvalidParam("File %s not found" % fe_id,
                                   "files")
        if file_ext.file.path is None:
            raise HTTPInvalidParam("File with hash %s should be ("
                                   "re)uploaded" %
                                   file_ext.file.sha256,
                                   "files")
        if file_ext.scan is not None:
            raise HTTPInvalidParam("File %s already scanned" %
                                   fe_id,
                                   "files")
        files_ext.append(file_ext)

    scan = Scan(compat.timestamp(), ip,
                force=force, mimetype_filtering=mimetype_filtering,
                resubmit_files=resubmit_files, files_ext=files_ext,
                probes=probes)
    session.add(scan)
    session.commit()
    # launch_asynchronous scan via frontend task
    celery_frontend.scan_launch(str(scan.external_id))

    return scan_schema.dump(scan).data


@hug.post("/{scan_id}/cancel")
def cancel(scan_id: uuid):
    """ Cancel a scan.
        The request should be performed using a POST request method.
    """
    log.debug("scan %s: cancel", scan_id)
    session = db.session
    scan = Scan.load_from_ext_id(scan_id, session)

    scan_ctrl.cancel(scan, session)

    return scan_schema.dump(scan).data


@hug.post("/{scan_id}/files", versions=1,
          input_format=hug.input_format.multipart)
def add_files(request, scan_id: uuid):
    """ Attach a file to a scan.
        The request should be performed using a POST request method.
    """
    log.debug("scan %s: add_files", scan_id)
    session = db.session
    scan = Scan.load_from_ext_id(scan_id, session)
    IrmaScanStatus.filter_status(scan.status,
                                 IrmaScanStatus.empty,
                                 IrmaScanStatus.ready)

    # request._params is init by Falcon
    form_dict = request._params
    if len(form_dict) == 0:
        raise HTTPInvalidParam("Empty list", "files")

    for (_, f) in form_dict.items():
        # Multipart Middleware giving a dict of uploaded files
        filename = decode_utf8(f.filename)
        # ByteIO object is in file
        data = f.file
        log.debug("scan %s: add filename: %s", scan_id, filename)
        file = File.get_or_create(data, session)
        # Legacy v1.1 as we dont received a submitter parameter
        # choose one from FileCli/FileWeb based on path value
        (path, name) = ntpath.split(filename)
        if path != "":
            file_ext = FileCli(file, filename)
        else:
            file_ext = FileWeb(file, filename)
        session.add(file_ext)
        file_ext.scan = scan
        session.commit()
    scan.set_status(IrmaScanStatus.ready)
    session.commit()

    return scan_schema.dump(scan).data


@hug.post("/{scan_id}/results")
def get_results(scan_id: uuid):
    """ Retrieve results for a scan. Results are the same as in the get()
        method, i.e. a summary for each scanned files.
        The request should be performed using a GET request method.
    """
    log.debug("scan %s: get_results", scan_id)
    session = db.session
    scan = Scan.load_from_ext_id(scan_id, session)

    schema = FileExtSchema(exclude=('probe_results',
                                    'file_infos'))
    return schema.dump(scan.files_ext, many=True).data


@hug.post("/quick", versions=2)
def quick_scan(request):
    """ Launch a scan for one file
    """
    session = db.session
    ip = request.remote_addr

    # Create file
    fe = files_ctrl.create(request)
    fe = FileExt.load_from_ext_id(fe['result_id'], session)

    # Create a scan
    scan = Scan(compat.timestamp(), ip, files_ext=[fe, ])
    session.add(scan)
    session.commit()

    # launch_asynchronous scan via frontend task
    celery_frontend.scan_launch(str(scan.external_id))

    return scan_schema.dump(scan).data
