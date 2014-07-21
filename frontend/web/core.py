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
import hashlib

import celery
import config.parser as config
from frontend import sqlobjects
from frontend.nosqlobjects import ProbeRealResult
from frontend.sqlobjects import Scan, File, FileWeb, ProbeResult
from lib.common import compat
from lib.irma.common.utils import IrmaReturnCode, IrmaScanStatus, \
    IrmaProbeResultsStates, IrmaScanResults
from lib.irma.common.exceptions import IrmaDatabaseError, \
    IrmaDatabaseResultNotFound
from frontend.format import IrmaProbeType, IrmaFormatter


sqlobjects.connect()

# =====================
#  Frontend Exceptions
# =====================
from lib.irma.database.sqlhandler import SQLDatabase


class IrmaFrontendWarning(Exception):
    pass


class IrmaFrontendError(Exception):
    pass


# ================
#  Task functions
# ================

cfg_timeout = config.get_brain_celery_timeout()

frontend_app = celery.Celery('frontendtasks')
config.conf_frontend_celery(frontend_app)

scan_app = celery.Celery('scantasks')
config.conf_brain_celery(scan_app)


def _task_probe_list():
    """ send a task to the brain asking for active probe list """
    try:
        task = scan_app.send_task("brain.tasks.probe_list", args=[])
        (status, res) = task.get(timeout=cfg_timeout)
        if status == IrmaReturnCode.error:
            raise IrmaFrontendError(res)
        elif status == IrmaReturnCode.warning:
            raise IrmaFrontendWarning(res)
        return res
    except celery.exceptions.TimeoutError:
        raise IrmaFrontendError("Celery timeout - probe_list")


def _task_scan_progress(scanid):
    """ send a task to the brain asking for status of subtasks launched """
    try:
        task = scan_app.send_task("brain.tasks.scan_progress", args=[scanid])
        (status, res) = task.get(timeout=cfg_timeout)
        return (status, res)
    except celery.exceptions.TimeoutError:
        raise IrmaFrontendError("Celery timeout - scan progress")


def _task_scan_cancel(scanid):
    """ send a task to the brain to cancel all remaining subtasks """
    try:
        task = scan_app.send_task("brain.tasks.scan_cancel", args=[scanid])
        (status, res) = task.get(timeout=cfg_timeout)
        return (status, res)
    except celery.exceptions.TimeoutError:
        raise IrmaFrontendError("Celery timeout - scan progress")

# =========
#  Helpers
# =========


def format_results(res_dict, filter_type):
    # - filter type is list of type returned
    res = {}
    for probe in res_dict.keys():
        # old results format
        # FIXME: remove this if db is cleaned
        if 'probe_res' in res_dict[probe]:
            probe_res = res_dict[probe]['probe_res']
        else:
            probe_res = res_dict[probe]
        format_res = IrmaFormatter.format(probe, probe_res)
        if filter_type is not None:
            # filter by type
            filter_str = [IrmaProbeType.label[ft] for ft in filter_type]
            if 'type' in format_res and \
               format_res['type'] not in filter_str:
                continue
        res[probe] = format_res
    return res


# ==================
#  Public functions
# ==================

def scan_new():
    """ Create new scan

    :rtype: str
    :return: scan id
    :raise: IrmaDataBaseError
    """
    #TODO get the ip
    scan = Scan(IrmaScanStatus.created, compat.timestamp(), None)
    scan.save()
    return scan.external_id


def scan_add(scanid, files):
    """ add file(s) to the specified scan

    :param scanid: id returned by scan_new
    :param files: dict of 'filename':str, 'data':str
    :rtype: int
    :return: int - total number of files for the scan
    :raise: IrmaFrontendWarning If the scan has already been started
    """
    session = SQLDatabase.get_session()

    scan = Scan.load_from_ext_id(scanid, session)
    if scan.status != IrmaScanStatus.created:
        # Cannot add file to a launched scan
        raise IrmaFrontendWarning(IrmaScanStatus.label[scan.status])
    for (name, data) in files.items():
        try:
            # The file exists
            file = File.load_from_sha256(hashlib.sha256(data).hexdigest(), session)
        except IrmaDatabaseResultNotFound:
            # It doesn't
            time = compat.timestamp()
            file = File(time, time)
            file.save(session)
            file.save_file_to_fs(data)
            file.update(session=session)

        file_web = FileWeb(file, name, scan)
        file_web.save(session)

    session.commit()
    return len(scan.files_web)


def scan_launch(scanid, force, probelist):
    """ launch specified scan

    :param scanid: id returned by scan_new
    :rtype: dict of 'code': int, 'msg': str [, optional 'probe_list':list]
    :return:
        on success 'probe_list' is the list of probes used for the scan
        on error 'msg' gives reason message
    :raise: IrmaDataBaseError, IrmaFrontendError
    """
    session = SQLDatabase.get_session()

    scan = Scan.load_from_ext_id(scanid, session)
    if scan.status != IrmaScanStatus.created:
        # Cannot launch scan with other status
        raise IrmaFrontendWarning(IrmaScanStatus.label[scan.status])
    all_probe_list = _task_probe_list()
    if len(all_probe_list) == 0:
        scan.status = IrmaScanStatus.finished
        scan.update(['status'], session=session)
        session.commit()
        raise IrmaFrontendError("No probe available")
    if probelist is not None:
        unknown_probes = []
        for p in probelist:
            if p not in all_probe_list:
                unknown_probes.append(p)
        if len(unknown_probes) != 0:
            reason = "Probe {0} unknown".format(", ".join(unknown_probes))
            scan.status = IrmaScanStatus.cancelled
            scan.update(['status'], session=session)
            session.commit()
            raise IrmaFrontendError(reason)
    else:
        # all available probes
        probelist = all_probe_list

    for fw in scan.files_web:
        for p in probelist:
            #TODO probe types
            scan_result = ProbeResult(
                None,
                p,
                None,
                IrmaProbeResultsStates.created,
                IrmaScanStatus.created,
                file_web=fw
            )
            scan_result.save(session=session)

    session.commit()

    # launch scan via frontend task
    frontend_app.send_task("frontend.tasks.scan_launch", args=(scan.id, force))
    return probelist


def scan_result(scanid):
    """ get results from files of specified scan

    :param scanid: id returned by scan_new
    :rtype: dict of sha256 value: dict of ['filename':str,
        'results':dict of [str probename: dict of [probe_type: str,
        status: int [, optional duration: int, optional result: int,
        optional results of probe]]]]
    :return:
        dict of results for each hash value
    :raise: IrmaDataBaseError
    """
    scan = Scan.load_from_ext_id(scanid)
    res = {}
    for fw in scan.files_web:
        probe_results = {}
        for pr in fw.probe_results:
            if pr.no_sql_id is None:  # An error occurred in the process
                probe_results[pr.probe_name] = {
                    'probe_type': pr.probe_type,
                    'status': pr.status
                }
            else:
                probe_results[pr.probe_name] = ProbeRealResult(
                    id=pr.no_sql_id
                ).get_results()
        res[fw.file.sha256] = {
            'filename': fw.name,
            'results': format_results(probe_results, None)
        }

    return res


def scan_progress(scanid):
    """ get scan progress for specified scan

    :param scanid: id returned by scan_new
    :rtype: dict of 'total':int, 'finished':int, 'successful':int
    :return:
        dict with total/finished/succesful jobs submitted by irma-brain
    :raise: IrmaDatabaseError, IrmaFrontendWarning, IrmaFrontendError
    """
    session = SQLDatabase.get_session()

    scan = Scan.load_from_ext_id(scanid, session=session)
    if scan.status != IrmaScanStatus.launched:
        # If not launched answer directly
        # Else ask brain for job status
        raise IrmaFrontendWarning(IrmaScanStatus.label[scan.status])
    (status, res) = _task_scan_progress(scanid)
    if status == IrmaReturnCode.success:
        return res
    elif status == IrmaReturnCode.warning:
        # if scan is processed for the brain,
        # it means all probes jobs are completed
        # we are just waiting for results
        if res == IrmaScanStatus.processed:
            scan.status(IrmaScanStatus.processed)
            scan.update(['status'], session=session)
            session.commit()
        raise IrmaFrontendWarning(IrmaScanStatus.label[res])
    else:
        raise IrmaFrontendError(res)


def scan_cancel(scanid):
    """ cancel all remaining jobs for specified scan

    :param scanid: id returned by scan_new
    :rtype: dict of 'cancel_details': total':int, 'finished':int,
        'cancelled':int
    :return:
        informations about number of cancelled jobs by irma-brain
    :raise: IrmaDatabaseError, IrmaFrontendWarning, IrmaFrontendError
    """
    session = SQLDatabase.get_session()

    scan = Scan.load_from_ext_id(scanid, session=session)
    if scan.status != IrmaScanStatus.launched:
        # If not launched answer directly
        # Else ask brain for job status
        scan.status = IrmaScanStatus.cancelled
        scan.update(['status'], session=session)
        session.commit()
        raise IrmaFrontendWarning(IrmaScanStatus.label[scan.status])

    (status, res) = _task_scan_cancel(scanid)
    if status == IrmaReturnCode.success:
        scan.status = IrmaScanStatus.cancelled
        scan.update(['status'], session=session)
        session.commit()
        return res
    elif status == IrmaReturnCode.warning:
        # if scan is finished for the brain
        # it means we are just waiting for results
        if res == IrmaScanStatus.processed:
            scan.status = IrmaScanStatus.processed
            scan.update(['status'], session=session)
            session.commit()
        raise IrmaFrontendWarning(IrmaScanStatus.label[res])
    else:
        raise IrmaFrontendError(res)


def scan_finished(scanid):
    """ return a boolean  indicating if scan is finished
    :param scanid: id returned by scan_new
    :rtype: boolean
    :return:
        True if scan is finished
        False otherwise
    :raise: IrmaDatabaseError, IrmaFrontendWarning, IrmaFrontendError
    """
    scan = Scan.load_from_ext_id(scanid)
    return scan.status == IrmaScanStatus.finished


def probe_list():
    """ get active probe list

    :rtype: list of str
    :return:
        list of probes names
    :raise: IrmaFrontendWarning, IrmaFrontendError
    """
    return _task_probe_list()


def file_exists(sha256):
    """ return results for file with given sha256 value

    :rtype: boolean
    :return:
        if exists returns True else False
    :raise: IrmaFrontendError
    """
    try:
        File.load_from_sha256(sha256=sha256)
        return True
    except IrmaDatabaseResultNotFound:
        return False
    except IrmaDatabaseError as e:
        raise IrmaFrontendError(str(e))


def file_result(sha256, filter_type=None):
    """ return results for file with given sha256 value

    :rtype: dict of sha256 value: dict of ['filename':str,
        'results':dict of [str probename: dict of [probe_type: str,
        status: int , duration: int, result: int, results of probe]]]]
    :return:
        if exists returns all available scan results
        for file with given sha256 value
    :raise: IrmaFrontendError
    """
    try:
        f = File.load_from_sha256(sha256=sha256)
        ref_res = {}
        probe_results = {}
        for rr in f.ref_results:
            probe_results[rr.probe_name] = ProbeRealResult(
                id=rr.no_sql_id
            ).get_results()
        ref_res[f.sha256] = {
            'filename': f.get_file_names(),
            'results': format_results(probe_results, filter_type)
        }

        return ref_res
    except Exception as e:
        raise IrmaFrontendWarning(str(e))


def file_infected(sha256):
    """ return antivirus score for file with given sha256 value

    :rtype: dict of ['infected':boolean,
        'nb_scan':int, 'nb_detected': int ]
    :return:
        returns detection score for
        file with given sha256 value
    :raise: Exception
    """
    try:
        nb_scan = nb_detected = 0

        av_results = file_result(sha256, filter_type=[IrmaProbeType.antivirus])
        probe_res = av_results[sha256]['results']
        for res in probe_res.values():
            nb_scan += 1
            if res['result'] == IrmaScanResults.isMalicious:
                nb_detected += 1

        return {'infected': (nb_detected > 0),
                'nb_detected': nb_detected,
                'nb_scan': nb_scan}
    except Exception as e:
        raise IrmaFrontendWarning(str(e))
