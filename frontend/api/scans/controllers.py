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
from hug.types import number, smart_boolean, uuid, comma_separated_list
from falcon.errors import HTTPInvalidParam

import api.scans.services as scan_ctrl
import api.probes.services as probe_ctrl
import api.tasks.frontendtasks as celery_frontend
from api.common.middlewares import db
from api.files.models import File
from api.files_ext.models import FileExt, FileWeb, FileCli
from api.files_ext.schemas import FileExtSchema
from lib.common import compat
from lib.irma.common.exceptions import IrmaDatabaseResultNotFound
from lib.common.utils import decode_utf8
from lib.irma.common.utils import IrmaScanStatus
from .models import Scan
from .schemas import ScanSchema
import time

scan_schema = ScanSchema()
log = logging.getLogger(__name__)


@hug.get("/")
def list(offset: number=0,
         limit: number=5):
    """ Get a list of all scans which have been launched.
    """
    session = db.session
    log.debug("offset %s limit %s", offset, limit)
    base_query = Scan.query_joined(session)

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


@hug.post("/{scan_id}/launch", versions=1)
def launch_v1(scan_id: uuid,
              probes: comma_separated_list=None,
              force: smart_boolean=False,
              mimetype_filtering: smart_boolean=True,
              resubmit_files: smart_boolean=True,
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
        force = scan_options.get("force", False)
        if type(force) is not bool:
            raise HTTPInvalidParam("Should be boolean", "force")
        mimetype_filtering = scan_options.get("mimetype_filtering", True)
        if type(mimetype_filtering) is not bool:
            raise HTTPInvalidParam("Should be boolean",
                                   "mimetype_filtering")
        resubmit_files = scan_options.get("resubmit_files", True)
        if type(resubmit_files) is not bool:
            raise HTTPInvalidParam("Should be boolean",
                                   "resubmit_files")
        probes = scan_options.get("probes", None)

    session = db.session
    ip = request.remote_addr
    scan = Scan(compat.timestamp(), ip)
    session.add(scan)

    # handle scan parameter
    # cached results: "force" (default: True)
    scan.force = force

    # use mimetype for probelist: "mimetype_filtering" (default: True)
    scan.mimetype_filtering = mimetype_filtering

    # rescan file outputted from probes "resubmit_files" (default: True)
    scan.resubmit_files = resubmit_files

    scan.set_status(IrmaScanStatus.empty)
    session.commit()

    log.debug("scan %s: created", scan.external_id)

    msg = "scan %s: Force %s MimeF %s"
    msg += " Resub %s Probes %s"
    log.debug(msg, scan.external_id, scan.force, scan.mimetype_filtering,
              scan.resubmit_files, probes)

    for fe_id in files_list:
        log.info("scan %s adding file %s", scan.external_id,
                 fe_id)
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
        file_ext.scan = scan

    scan.set_status(IrmaScanStatus.ready)
    session.commit()

    probelist = probe_ctrl.check_probe(probes)
    scan.set_probelist(probelist)
    session.commit()
    # launch_asynchronous scan via frontend task
    celery_frontend.scan_launch(str(scan.external_id))

    return scan_schema.dump(scan).data

@hug.post("/scan" , versions=2)
def launch_vtapi_v2(request, body,
                    probes: comma_separated_list=None,
                    force: smart_boolean=False,
                    mimetype_filtering: smart_boolean=True,
                    resubmit_files: smart_boolean=True,
                    ):
    """ Launch a scam after adding the file Version 2.
        The request should be performed using a POST request method
        The sample curl command is as below
        {
            curl -v -F 'file=@/home/vagrant/test.log' \
              http://127.0.0.1/vtapi/v2/file/scan/
            options:
               probes: list of probes or None for all available, }
               force: boolean (default False),
               mimetype_filtering: boolean (default True),
               resubmit_files: boolean (default True),
        }
    """
    log.info("Entering version2 scan method")
    session = db.session
    ip = request.remote_addr
    scan = Scan(compat.timestamp(), ip)
    session.add(scan)
    log.info("Session created and scan added")
    scan.set_status(IrmaScanStatus.empty)
    session.commit()
    log.info("scan %s: created", scan.external_id)
    msg = str(type(scan.external_id))
    msg = str(scan.external_id)
    scan_id = uuid(scan.external_id)
    log.info(str(scan_id))
    add_files_v2(request, scan_id)
    launch_v1(scan_id, probes, force)
    time.sleep(5)
    session.refresh(scan)
    if not scan.files:
        file_md5 = 'File not present'
        file_sha256 = 'File not present'
    else:
        file_md5 = scan.files[0].md5
        file_sha256 = scan.files[0].sha256
    results_check = scan_schema.dump(scan).data
    return {
        "response_code": status_code(results_check['force'],
                                     results_check['probes_finished'],
                                     results_check['probes_total']),
        "scan_id": str(scan_id),
        "sha256": file_sha256,
        "permalink": "http;//frontend.irma/scan/"+str(scan_id),
        "verbose_msg": status_msg(results_check['force'],
                                  results_check['probes_finished'],
                                  results_check['probes_total']),
        "resource": file_md5
    }


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

def add_files_v2(request, scan_id: uuid):
    log.debug("scan %s: add_files", scan_id)
    session = db.session
    scan = Scan.load_from_ext_id(scan_id, session)
    IrmaScanStatus.filter_status(scan.status,
                                 IrmaScanStatus.empty,
                                 IrmaScanStatus.ready)
    req_dict = request.get_param_as_list('file')
    if len(req_dict) == 0:
        raise HTTPInvalidParam("Empty list", "files")
    for f in req_dict:
        filename = decode_utf8(f.filename)
        data = f.file
        log.debug("scan %s: add filename: %s", scan_id, filename)
        file = File.get_or_create(data, session)
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


def status_code(context_force, probes_finished, probes_total):
    try:
        if context_force is True:
            return 0
        if probes_finished == probes_total and probes_total != 0:
            return 1
        if probes_finished != probes_total and probes_total != 0:
            return 0
        else:
            return -1
    except Exception as e:
        return -1

def status_msg(context_force, probes_finished, probes_total):
    try:
        if context_force is True:
            return "Scan request successfully queued, " \
                "come back later for the report"
        if probes_finished == probes_total and probes_total != 0:
            return "Scan finished, scan information available"
        if probes_finished != probes_total and probes_total != 0:
            return "Scan request successfully queued, " \
                "come back later for the report"
        else:
            return "Scan can't be queued, there is an error"
    except Exception as e:
        return "Scan can't be queued, there is an error"

@hug.post("/report", versions=2)
def get_report(request, scan_id: hug.types.uuid):
    """Retrieve the report from the provided resource"""
    session = db.session
    scan = Scan.load_from_ext_id(scan_id, session)
    scan_schema = ScanSchema()
    result_list = []
    log.info(scan_schema.dump(scan).data)
    for item in scan.files_ext:
        for res in item.probe_results:
            result_list.append(res.get_details())
    positive_count = 0
    for r in result_list:
        if r['results'] is not None:
            positive_count += 1
    final_list = []
    for d in result_list:
        res_dict = {k: d[k] for k in ('results', 'duration',
                                      'virus_database_version',
                                      'version', 'type')}
        final_dict = {d['name']: res_dict}
        final_list.append(final_dict.copy())
    return {
        "scan_id": str(scan_id),
        "scans": final_list,
        "total": scan.probes_total,
        "resource": scan.files[0].md5,
        "sha256": scan.files[0].sha256,
        "scan_date": time.strftime('%Y-%m-%d %H:%M:%S',
                                   time.localtime(scan.date)),
        "md5": scan.files[0].md5,
        "sha1": scan.files[0].sha1,
        "response_code": report_code(scan.probes_finished, scan.probes_total),
        "verbose_msg": report_msg(scan.probes_finished, scan.probes_total),
        "positives": positive_count,
    }

def report_code(probes_finished, probes_total):
    try:
        if probes_finished == probes_total and probes_total != 0:
            return 1
        if probes_finished != probes_total and probes_total != 0:
            return 0
        else:
            return -1
    except Exception as e:
        return -1


def report_msg(probes_finished, probes_total):
    try:
        if probes_finished == probes_total and probes_total != 0:
            return "Scan finished, scan information embedded in this object"
        if probes_finished != probes_total and probes_total != 0:
            return "Scan request successfully queued, " \
                "come back later for the report"
        else:
            return "Scan can't be queued, there is an error"
    except Exception as e:
        return "Scan can't be queued, there is an error"


@hug.post("/rescan", versions=2)
def rescan_files(request, body):
    return launch_vtapi_v2(request, body, None, True)
