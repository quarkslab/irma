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

import re
import os
import bottle
import importlib
import json
import sys
import logging

from bottle import route, request, default_app, run, abort
from lib.common.utils import UUID

"""
    IRMA FRONTEND WEB API
    defines all accessible route accessed via uwsgi..
"""

from lib.irma.common.utils import IrmaFrontendReturn
from lib.irma.common.exceptions import IrmaTaskError, IrmaValueError
import frontend.controllers.scanctrl as scan_ctrl
import frontend.controllers.filectrl as file_ctrl


# =============
#  Server root
# =============

@route("/")
def svr_index():
    """ hello world

    :route: /
    :rtype: dict of 'code': int, 'msg': str
    :return: on success 'code' is 0
    """
    return IrmaFrontendReturn.success()


# =====================
#  Common param checks
# =====================

def _valid_id(scanid):
    """ check scanid format - should be UUID"""
    if not UUID.validate(scanid):
        raise IrmaValueError("not a valid Scanid")


def _valid_sha256(sha256):
    """ check hashvalue format - should be a sha256 hexdigest"""
    if not re.match(r'^[0-9a-fA-F]{64}$', sha256):
        raise IrmaValueError("noe a valid sha256")


# ==========
#  Scan api
# ==========

@route("/scan/new")
def scan_new():
    """ create new scan

    :route: /scan/new
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


@route("/scan/add/<scanid>", method='POST')
def scan_add(scanid):
    """ add posted file(s) to the specified scan

    :route: /scan/add/<scanid>
    :postparam: multipart form with filename(s) and file(s) data
    :param scanid: id returned by scan_new
    :note: files are posted as multipart/form-data
    :rtype: dict of 'code': int, 'msg': str [, optional 'nb_files':int]
    :return:
        on success 'nb_files' total number of files for the scan
        on error 'msg' gives reason message
    """
    try:
        # Filter malformed scanid
        _valid_id(scanid)
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


@route("/scan/launch/<scanid>", method='GET')
def scan_launch(scanid):
    """ launch specified scan

    :route: /scan/launch/<scanid>
    :getparam: force=True or False
    :getparam: probe=probe1,probe2
    :param scanid: id returned by scan_new
    :rtype: dict of 'code': int, 'msg': str [, optional 'probe_list':list]
    :return:
        on success 'probe_list' is the list of probes used for the scan
        on error 'msg' gives reason message
    """
    try:
        # Filter malformed scanid
        _valid_id(scanid)
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


@route("/scan/result/<scanid>", method='GET')
def scan_result(scanid):
    """ get all results from files of specified scan

    :route: /scan/result/<scanid>
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
        # Filter malformed scanid
        _valid_id(scanid)
        results = scan_ctrl.result(scanid)
        return IrmaFrontendReturn.success(scan_results=results)
    except IrmaValueError as e:
        return IrmaFrontendReturn.warning(str(e))
    except Exception as e:
        return IrmaFrontendReturn.error(str(e))


@route("/scan/progress/<scanid>", method='GET')
def scan_progress(scanid):
    """ get scan progress for specified scan

    :route: /scan/progress/<scanid>
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
        # Filter malformed scanid
        _valid_id(scanid)
        progress = scan_ctrl.progress(scanid)
        return IrmaFrontendReturn.success(progress_details=progress)
    except IrmaValueError as e:
        return IrmaFrontendReturn.warning(str(e))
    except Exception as e:
        return IrmaFrontendReturn.error(str(e))


@route("/scan/cancel/<scanid>", method='GET')
def scan_cancel(scanid):
    """ cancel all remaining jobs for specified scan

    :route: /scan/cancel/<scanid>
    :param scanid: id returned by scan_new
    :rtype: dict of 'code': int, 'msg': str
        [, optional 'cancel_details':
            'total':int,
            'finished':int,
            'cancelled':int]
    :return:
        on success 'cancel_details' contains informations \
        about cancelled jobs by irma-brain
        on warning 'msg' gives scan status that make it not cancellable
        on error 'msg' gives reason message
    """
    # Filter malformed scanid
    if not _valid_id(scanid):
        return IrmaFrontendReturn.error("not a valid scanid")
    try:
        cancel = scan_ctrl.cancel(scanid)
        return IrmaFrontendReturn.success(cancel_details=cancel)
    except IrmaValueError as e:
        return IrmaFrontendReturn.warning(str(e))
    except Exception as e:
        return IrmaFrontendReturn.error(str(e))


@route("/scan/finished/<scanid>", method='GET')
def scan_finished(scanid):
    """ tell if scan specified is finished

    :route: /scan/finished/<scanid>
    :param scanid: id returned by scan_new
    :rtype: dict of 'code': int, 'msg': str
    :return:
        on success results are ready
        on warning 'msg' gives current scan status
        on error 'msg' gives reason message
    """
    try:
        # Filter malformed scanid
        _valid_id(scanid)
        if scan_ctrl.finished(scanid):
            return IrmaFrontendReturn.success(msg="finished")
        else:
            return IrmaFrontendReturn.warning("not finished")
    except Exception as e:
        return IrmaFrontendReturn.error(str(e))


# ===========
#  Probe api
# ===========

@route("/probe/list")
def probe_list():
    """ get active probe list

    :route: /probe/list
    :rtype: dict of 'code': int, 'msg': str
        [, optional 'probe_list': list of str]
    :return:
        on success 'probe_list' contains list of probes names
        on error 'msg' gives reason message
    """
    try:
        probelist = scan_ctrl.probe_list()
        return IrmaFrontendReturn.success(probe_list=probelist)
    except Exception as e:
        return IrmaFrontendReturn.error(str(e))


# ==========
#  File api
# ==========
@route("/file/exists/<sha256>")
def file_exists(sha256):
    """ lookup file by sha256 and tell if it exists

    :route: /file/exists/<sha256>
    :param sha256 of the file
    :rtype: dict of 'code': int, 'msg': str
        [, optional 'exists':boolean]
    :return:
        on success 'exists' contains a boolean telling if
        file exists or not
        on error 'msg' gives reason message
    """
    # Filter malformed scanid
    if not _valid_sha256(sha256):
        return IrmaFrontendReturn.error("not a valid sha256")
    try:
        exists = file_ctrl.exists(sha256)
        return IrmaFrontendReturn.success(exists=exists)
    except Exception as e:
        return IrmaFrontendReturn.error(str(e))


@route("/file/result/<sha256>")
def file_result(sha256):
    """ lookup file by sha256

    :route: /file/search/<scanid>
    :param sha256 of the file
    :rtype: dict of 'code': int, 'msg': str
        [, optional 'scan_results': dict of [
            sha256 value: dict of
                'filenames':list of filename,
                'results': dict of [str probename: dict [results of probe]]]]
    :return:
        on success 'scan_results' contains results for file
        on error 'msg' gives reason message
    """
    # Filter malformed scanid
    if not _valid_sha256(sha256):
        return IrmaFrontendReturn.error("not a valid sha256")
    try:
        res = file_ctrl.result(sha256)
        return IrmaFrontendReturn.success(scan_results=res)
    # handle all errors/warning as errors
    # file existence should be tested before calling this route
    except Exception as e:
        return IrmaFrontendReturn.error(str(e))


@route("/file/infected/<sha256>")
def file_infected(sha256):
    """ lookup file by sha256 and tell if av detect it as
        infected

    :route: /file/suspicious/<sha256>
    :param sha256 of the file
    :rtype: dict of 'code': int, 'msg': str
        [, optional 'infected':boolean, 'nb_detected':int, 'nb_scan':int]
    :return:
        on success 'infected' contains boolean results
        with details in 'nb_detected' and 'nb_scan'
        on error 'msg' gives reason message
    """
    # Filter malformed scanid
    if not _valid_sha256(sha256):
        return IrmaFrontendReturn.error("not a valid sha256")
    try:
        res = file_ctrl.infected(sha256)
        return IrmaFrontendReturn.success(infected=res['infected'],
                                          nb_scan=res['nb_scan'],
                                          nb_detected=res['nb_detected'])
    except Exception as e:
        return IrmaFrontendReturn.error(str(e))

application = default_app()
