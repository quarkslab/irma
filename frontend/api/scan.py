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
from bottle import Bottle, request
from lib.common.utils import UUID
from lib.irma.common.utils import IrmaFrontendReturn
import frontend.controllers.scanctrl as scan_ctrl


scan_app = Bottle()


# =====================
#  Common param checks
# =====================

def validate_id(scanid):
    """ check scanid format - should be a str(ObjectId)"""
    if not UUID.validate(scanid):
        raise ValueError("Malformed Scanid")


# ==========
#  Scan api
# ==========

@scan_app.route("/new")
def new():
    """ create new scan

    :route: /new
    :rtype: dict of 'code': int, 'msg': str [, optional 'scan_id':str]
    :return:
        on success 'scan_id' contains the newly created scan id
        on error 'msg' gives reason message
    """
    try:
        scan_id = scan_ctrl.new()
        return IrmaFrontendReturn.success(scan_id=scan_id)
    except Exception as e:
        return IrmaFrontendReturn.error(str(e))


@scan_app.route("/add/<scanid>", method='POST')
def add(scanid):
    """ add posted file(s) to the specified scan

    :route: /add/<scanid>
    :postparam: multipart form with filename(s) and file(s) data
    :param scanid: id returned by scan_new
    :note: files are posted as multipart/form-data
    :rtype: dict of 'code': int, 'msg': str [, optional 'nb_files':int]
    :return:
        on success 'nb_files' total number of files for the scan
        on error 'msg' gives reason message
    """
    try:
        validate_id(scanid)
        files = {}
        for f in request.files:
            upfile = request.files.get(f)
            filename = os.path.basename(upfile.filename)
            data = upfile.file.read()
            files[filename] = data
        nb_files = scan_ctrl.add_files(scanid, files)
        return IrmaFrontendReturn.success(nb_files=nb_files)
    except Exception as e:
        return IrmaFrontendReturn.error(str(e))


@scan_app.route("/launch/<scanid>", method='GET')
def launch(scanid):
    """ launch specified scan

    :route: /launch/<scanid>
    :getparam: force=True or False
    :getparam: probe=probe1,probe2
    :param scanid: id returned by scan_new
    :rtype: dict of 'code': int, 'msg': str [, optional 'probe_list':list]
    :return:
        on success 'probe_list' is the list of probes used for the scan
        on error 'msg' gives reason message
    """
    try:
        validate_id(scanid)
        # handle 'force' parameter
        force = False
        if 'force' in request.params:
            if request.params['force'].lower() == 'true':
                force = True
        # handle 'probe' parameter
        in_probelist = None
        if 'probe' in request.params:
            in_probelist = request.params['probe'].split(',')
        out_probelist = scan_ctrl.launch(scanid, force, in_probelist)
        return IrmaFrontendReturn.success(probe_list=out_probelist)
    except Exception as e:
        return IrmaFrontendReturn.error(str(e))


@scan_app.route("/result/<scanid>", method='GET')
def result(scanid):
    """ get all results from files of specified scan

    :route: /result/<scanid>
    :param scanid: id returned by scan_new
    :rtype: dict of 'code': int, 'msg': str
        [, optional 'scan_results': dict of [
            sha256 value: dict of
                'filenames':list of filename,
                'results': dict of [str probename: dict [results of probe]]]]
    :return:
        on success 'scan_results' is the dict of results for each filename
        on error 'msg' gives reason message
    """
    try:
        validate_id(scanid)
        results = scan_ctrl.result(scanid)
        return IrmaFrontendReturn.success(scan_results=results)
    except Exception as e:
        return IrmaFrontendReturn.error(str(e))


@scan_app.route("/progress/<scanid>", method='GET')
def progress(scanid):
    """ get scan progress for specified scan

    :route: /progress/<scanid>
    :param scanid: id returned by scan_new
    :rtype: dict of 'code': int, 'msg': str
        [, optional 'progress_details':
            'total':int,
            'finished':int,
            'successful':int]
    :return:
        on success 'progress_details' contains informations \
        about submitted jobs by irma-brain
        on warning 'msg' gives scan status that does not required \
        progress_details like 'processed' or 'finished'
        on error 'msg' gives reason message
    """
    try:
        validate_id(scanid)
        progress = scan_ctrl.progress(scanid)
        details = progress.get('progress_details', None)
        if details is not None:
            return IrmaFrontendReturn.success(progress_details=details)
        else:
            return IrmaFrontendReturn.warning(progress['status'])
    except Exception as e:
        return IrmaFrontendReturn.error(str(e))


@scan_app.route("/cancel/<scanid>", method='GET')
def scan_cancel(scanid):
    """ cancel all remaining jobs for specified scan

    :route: /cancel/<scanid>
    :param scanid: id returned by scan_new
    :rtype: dict of 'code': int, 'msg': str
        [, optional 'cancel_details':
            'total':int,
            'finished':int,
            'cancelled':int]
    :return:
        on success 'cancel_details' contains informations \
        about cancelled jobs by irma-brain
        on error 'msg' gives reason message
    """
    try:
        validate_id(scanid)
        cancel = scan_ctrl.cancel(scanid)
        return IrmaFrontendReturn.success(cancel_details=cancel)
    except Exception as e:
        return IrmaFrontendReturn.error(str(e))


@scan_app.route("/finished/<scanid>", method='GET')
def finished(scanid):
    """ tell if scan specified is finished

    :route: /finished/<scanid>
    :param scanid: id returned by scan_new
    :rtype: dict of 'code': int, 'msg': str
    :return:
        on success results are ready
        on error 'msg' gives reason message
    """
    try:
        validate_id(scanid)
        if scan_ctrl.finished(scanid):
            return IrmaFrontendReturn.success(msg="finished")
        else:
            return IrmaFrontendReturn.warning("not finished")
    except Exception as e:
        return IrmaFrontendReturn.error(str(e))
