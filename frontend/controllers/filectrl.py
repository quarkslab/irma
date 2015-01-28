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

from frontend.models.sqlobjects import File, FileWeb
from frontend.models.nosqlobjects import ProbeRealResult
from lib.irma.common.exceptions import IrmaDatabaseResultNotFound, \
    IrmaDatabaseError, IrmaTaskError
from lib.irma.common.utils import IrmaProbeType
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


def query_find_by_hash(hash_type, hash_value):
    with session_query() as session:
        try:
            return FileWeb.query_find_by_hash(hash_type, hash_value, session)
        except IrmaDatabaseError as e:
            raise IrmaTaskError(str(e))


def query_find_by_name(name, strict):
    with session_query() as session:
        try:
            return FileWeb.query_find_by_name(name, strict, session)
        except IrmaDatabaseError as e:
            raise IrmaTaskError(str(e))


def get_results(sha256, formatted, filter_type=None):
    """ return results for file with given sha256 value
        results are formatted or not according to formatted parameter

    :param sha256: digest of the file
    :param formatted: boolean for filterting results or not
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
            if filter_type is not None and rr.type not in filter_type:
                continue
            probe_results[rr.name] = ProbeRealResult(
                id=rr.nosql_id
            ).to_json(formatted)
        ref_res[f.sha256] = {}
        ref_res[f.sha256]['filename'] = f.get_file_names()
        ref_res[f.sha256]['results'] = probe_results
        return ref_res


def infected(sha256):
    """ return antivirus score for file with given sha256 value

    :rtype: dict of ['infected':boolean,
        'nb_scan':int, 'nb_detected': int ]
    :return:
        returns detection score for
        file with given sha256 value
    """
    av_results = get_results(sha256, True, filter_type=[IrmaProbeType.antivirus])
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
