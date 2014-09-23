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

from frontend.models.sqlobjects import File
from frontend.models.nosqlobjects import ProbeRealResult
from lib.irma.common.exceptions import IrmaDatabaseResultNotFound, \
    IrmaDatabaseError, IrmaTaskError
from lib.irma.common.utils import IrmaProbeType
from .scanctrl import format_results
from frontend.helpers.sql import session_query


def init_by_sha256(sha256):
    """ return results for file with given sha256 value

    :rtype: boolean
    :return:
        if exists returns sha256 value else None
    :raise: IrmaTaskError
    """
    with session_query() as session:
        try:
            f = File.load_from_sha256(sha256, session)
            return f.sha256
        except IrmaDatabaseResultNotFound:
            return None
        except IrmaDatabaseError as e:
            raise IrmaTaskError(str(e))


def init_by_sha1(sha1):
    """ return results for file with given sha1 value

    :rtype: boolean
    :return:
        if exists returns sha256 value else None
    :raise: IrmaTaskError
    """
    with session_query() as session:
        try:
            f = File.load_from_sha1(sha1, session)
            return f.sha256
        except IrmaDatabaseResultNotFound:
            return None
        except IrmaDatabaseError as e:
            raise IrmaTaskError(str(e))


def init_by_md5(md5):
    """ return results for file with given sha256 value

    :rtype: boolean
    :return:
        if exists returns True else False
    :raise: IrmaTaskError
    """
    with session_query() as session:
        try:
            f = File.load_from_md5(md5, session)
            return f.sha256
        except IrmaDatabaseResultNotFound:
            return False
        except IrmaDatabaseError as e:
            raise IrmaTaskError(str(e))


def find_by_name(name, strict, page, page_size, order_by, fields, desc):
    with session_query() as session:
        try:
            res = File.find_by_name(name, strict, page, page_size,
                                    order_by, fields, desc, session)
            return res
        except IrmaDatabaseError as e:
            raise IrmaTaskError(str(e))


def result(sha256, filter_type=None):
    """ return results for file with given sha256 value

    :rtype: dict of sha256 value: dict of ['filename':str,
        'results':dict of [str probename: dict of [probe_type: str,
        status: int , duration: int, result: int, results of probe]]]]
    :return:
        if exists returns all available scan results
        for file with given sha256 value
    """
    with session_query() as session:
        # TODO handle file dont exists here
        f = File.load_from_sha256(sha256, session)
        ref_res = {}
        probe_results = {}
        for rr in f.ref_results:
            probe_results[rr.probe_name] = ProbeRealResult(
                id=rr.nosql_id
            ).get_results()
        ref_res[f.sha256] = {
            'filename': f.get_file_names(),
            'results': format_results(probe_results, filter_type)
        }
        return ref_res


def infected(sha256):
    """ return antivirus score for file with given sha256 value

    :rtype: dict of ['infected':boolean,
        'nb_scan':int, 'nb_detected': int ]
    :return:
        returns detection score for
        file with given sha256 value
    """
    av_results = result(sha256, filter_type=[IrmaProbeType.antivirus])
    probe_res = av_results[sha256]['results']
    nb_scan = nb_detected = 0
    for res in probe_res.values():
        nb_scan += 1
        # TODO export Antivirus.ScanResults values
        if res['status'] == 1:
            nb_detected += 1

    return {'infected': (nb_detected > 0),
            'nb_detected': nb_detected,
            'nb_scan': nb_scan}


def remove_files(max_age_sec):
    with session_query() as session:
        return File.remove_old_files(max_age_sec, session)
