#
# Copyright (c) 2013-2014 QuarksLab.
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
from bottle import response, request
from lib.common import compat
from lib.irma.common.utils import IrmaScanStatus
from frontend.api.errors import process_error
from frontend.models.sqlobjects import Scan
from frontend.helpers.schemas import ScanSchema, FileWebSchema
from frontend.helpers.utils import validate_scanid
import frontend.controllers.scanctrl as scan_ctrl
import frontend.controllers.frontendtasks as celery_frontend


scan_schema = ScanSchema()


def list(db):
    """ Get a list of all scans which have been launched.
    """
    try:
        offset = int(request.query.offset) if request.query.offset else 0
        limit = int(request.query.limit) if request.query.limit else 5

        base_query = db.query(Scan)

        items = base_query.limit(limit).offset(offset).all()

        if offset == 0 and len(items) < limit:
            total = len(items)
        else:
            total = base_query.count()

        response.content_type = "application/json; charset=UTF-8"
        return {
            "total": total,
            "offset": offset,
            "limit": limit,
            "data": scan_schema.dump(items, many=True).data,
        }
    except Exception as e:
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

        response.content_type = "application/json; charset=UTF-8"
        return scan_schema.dumps(scan).data
    except Exception as e:
        process_error(e)


def get(scanid, db):
    """ Retrieve information for a specific scan
    """
    try:
        validate_scanid(scanid)
        scan = Scan.load_from_ext_id(scanid, db)

        response.content_type = "application/json; charset=UTF-8"
        return scan_schema.dumps(scan).data
    except Exception as e:
        process_error(e)


def launch(scanid, db):
    """ Launch a scan.
        The request should be performed using a POST request method.
    """
    try:
        validate_scanid(scanid)
        scan = Scan.load_from_ext_id(scanid, db)

        force = False
        probes = None

        # handle scan parameter / cached results: "force"
        if 'force' in request.json and request.json.get('force'):
            force = True

        # handle scan parameter / probelist: "probes"
        if 'probes' in request.json:
            probes = request.json.get('probes').split(',')

        scan_ctrl.launch_synchronous(scan, force, probes, db)
        # launch_asynchronous scan via frontend task
        celery_frontend.scan_launch(scanid)

        response.content_type = "application/json; charset=UTF-8"
        return scan_schema.dumps(scan).data
    except Exception as e:
        process_error(e)


def cancel(scanid, db):
    """ Cancel a scan.
        The request should be performed using a POST request method.
    """
    try:
        validate_scanid(scanid)
        scan = Scan.load_from_ext_id(scanid, db)

        scan_ctrl.cancel(scan, db)

        response.content_type = "application/json; charset=UTF-8"
        return scan_schema.dumps(scan).data
    except Exception as e:
        process_error(e)


def add_files(scanid, db):
    """ Attach a file to a scan.
        The request should be performed using a POST request method.
    """
    try:
        validate_scanid(scanid)
        scan = Scan.load_from_ext_id(scanid, db)

        files = {}
        for f in request.files:
            upfile = request.files.get(f)
            filename = os.path.basename(upfile.filename)
            data = upfile.file.read()
            files[filename] = data

        scan_ctrl.add_files(scan, files, db)

        response.content_type = "application/json; charset=UTF-8"
        return scan_schema.dumps(scan).data
    except Exception as e:
        process_error(e)


def get_results(scanid, db):
    """ Retrieve results for a scan. Results are the same as in the get()
        method, i.e. a summary for each scanned files.
        The request should be performed using a POST request method.
    """
    try:
        validate_scanid(scanid)
        scan = Scan.load_from_ext_id(scanid, db)

        file_web_schema = FileWebSchema(exclude=('probe_results',
                                                 'file_infos'))

        response.content_type = "application/json; charset=UTF-8"
        return file_web_schema.dumps(scan.files_web, many=True).data
    except Exception as e:
        process_error(e)


def get_result(scanid, resultid, db):
    """ Retrieve a single result, with details.
        The request should be performed using a POST request method.
    """
    try:
        formatted = False if request.query.formatted == 'no' else True

        validate_scanid(scanid)
        scan = Scan.load_from_ext_id(scanid, db)

        for fw in scan.files_web:
            if fw.scan_file_idx == resultid:
                file_web = fw
                break

        file_web_schema = FileWebSchema()
        file_web_schema.context = {'formatted': formatted}

        response.content_type = "application/json; charset=UTF-8"
        return file_web_schema.dumps(file_web).data
    except Exception as e:
        process_error(e)
