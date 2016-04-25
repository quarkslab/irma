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

import os
import logging
from bottle import response, request
from lib.common import compat
from lib.common.utils import decode_utf8
from lib.irma.common.utils import IrmaScanStatus
from frontend.api.v1.errors import process_error
from frontend.models.sqlobjects import Scan, FileWeb
from frontend.api.v1.schemas import ScanSchema_v1, FileWebSchema_v1
from frontend.helpers.utils import validate_id
import frontend.controllers.scanctrl as scan_ctrl
import frontend.controllers.frontendtasks as celery_frontend


scan_schema = ScanSchema_v1()
log = logging.getLogger(__name__)


def list(db):
    """ Get a list of all scans which have been launched.
    """
    try:
        offset = int(request.query.offset) if request.query.offset else 0
        limit = int(request.query.limit) if request.query.limit else 5
        log.debug("offset %d limit %d", offset, limit)
        base_query = db.query(Scan)

        items = base_query.limit(limit).offset(offset).all()

        if offset == 0 and len(items) < limit:
            total = len(items)
        else:
            total = base_query.count()

        log.debug("found %d scans", total)
        response.content_type = "application/json; charset=UTF-8"
        return {
            "total": total,
            "offset": offset,
            "limit": limit,
            "data": scan_schema.dump(items, many=True).data,
        }
    except Exception as e:
        log.exception(e)
        process_error(e)


def new(db):
    """ Create a new scan.
        The request should be performed using a POST request method.
    """
    try:
        ip = request.remote_addr
        scan = Scan(compat.timestamp(), ip)
        db.add(scan)

        scan.set_status(IrmaScanStatus.empty)
        db.commit()
        log.debug("scanid: %s", scan.external_id)
        response.content_type = "application/json; charset=UTF-8"
        return scan_schema.dumps(scan).data
    except Exception as e:
        log.exception(e)
        process_error(e)


def get(scanid, db):
    """ Retrieve information for a specific scan
    """
    try:
        log.debug("scanid: %s", scanid)
        validate_id(scanid)
        scan = Scan.load_from_ext_id(scanid, db)

        response.content_type = "application/json; charset=UTF-8"
        return scan_schema.dumps(scan).data
    except Exception as e:
        log.exception(e)
        process_error(e)


def launch(scanid, db):
    """ Launch a scan.
        The request should be performed using a POST request method.
    """
    try:
        validate_id(scanid)
        scan = Scan.load_from_ext_id(scanid, db)
        probes = None

        # handle scan parameter / cached results: "force"
        if 'force' in request.json and request.json.get('force'):
            scan.force = True
            db.commit()

        # V1 retro compatibility
        scan.mimetype_filtering = False
        scan.file_resubmit = False

        # handle scan parameter / probelist: "probes"
        if 'probes' in request.json:
            probes = request.json.get('probes').split(',')

        msg = "scanid: %s Force %s MimeF %s"
        msg += "Resub %s Probes %s"
        log.debug(msg, scanid, scan.force, scan.mimetype_filtering,
                  scan.resubmit_files, probes)
        scan_ctrl.check_probe(scan, probes, db)
        # launch_asynchronous scan via frontend task
        celery_frontend.scan_launch(scanid)

        response.content_type = "application/json; charset=UTF-8"
        return scan_schema.dumps(scan).data
    except Exception as e:
        log.exception(e)
        process_error(e)


def cancel(scanid, db):
    """ Cancel a scan.
        The request should be performed using a POST request method.
    """
    try:
        log.debug("scanid: %s", scanid)
        validate_id(scanid)
        scan = Scan.load_from_ext_id(scanid, db)

        scan_ctrl.cancel(scan, db)

        response.content_type = "application/json; charset=UTF-8"
        return scan_schema.dumps(scan).data
    except Exception as e:
        log.exception(e)
        process_error(e)


def add_files(scanid, db):
    """ Attach a file to a scan.
        The request should be performed using a POST request method.
    """
    try:
        log.debug("scanid: %s", scanid)
        validate_id(scanid)
        scan = Scan.load_from_ext_id(scanid, db)

        if len(request.files) == 0:
            raise ValueError("No files uploaded")

        files = {}
        for f in request.files:
            upfile = request.files.get(f)
            filename = decode_utf8(upfile.raw_filename)
            data = upfile.file
            files[filename] = data

        scan_ctrl.add_files(scan, files, db)

        response.content_type = "application/json; charset=UTF-8"
        return scan_schema.dumps(scan).data
    except Exception as e:
        log.exception(e)
        process_error(e)


def get_results(scanid, db):
    """ Retrieve results for a scan. Results are the same as in the get()
        method, i.e. a summary for each scanned files.
        The request should be performed using a GET request method.
    """
    try:
        log.debug("scanid: %s", scanid)
        validate_id(scanid)
        scan = Scan.load_from_ext_id(scanid, db)
        file_web_schema = FileWebSchema_v1(exclude=('probe_results',
                                                    'file_infos'))
        response.content_type = "application/json; charset=UTF-8"
        return file_web_schema.dumps(scan.files_web, many=True).data
    except Exception as e:
        log.exception(e)
        process_error(e)


def get_result(scanid, resultid, db):
    """ Retrieve a single fileweb result, with details.
        The request should be performed using a GET request method.
    """
    try:
        log.debug("scanid: %s resultid %s", scanid, resultid)
        formatted = False if request.query.formatted == 'no' else True

        validate_id(resultid)
        fw = FileWeb.load_from_ext_id(resultid, db)

        file_web_schema = FileWebSchema_v1(exclude=('mimetype',
                                                    'file_sha256',
                                                    'parent_file_sha256'))
        file_web_schema.context = {'formatted': formatted}

        response.content_type = "application/json; charset=UTF-8"
        return file_web_schema.dumps(fw).data
    except Exception as e:
        log.exception(e)
        process_error(e)
