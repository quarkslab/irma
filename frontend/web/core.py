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

import celery
import config.parser as config
from frontend.objects import ScanInfo, ScanFile, ScanRefResults
from lib.irma.common.utils import IrmaReturnCode, IrmaScanStatus, IrmaLockMode
from lib.irma.common.exceptions import IrmaDatabaseError, \
    IrmaDatabaseResultNotFound, IrmaCoreError, IrmaValueError, IrmaTaskError


# =====================
#  Frontend Exceptions
# =====================

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
        (retcode, res) = task.get(timeout=cfg_timeout)
        if retcode != IrmaReturnCode.success:
            raise IrmaTaskError(res)
        if len(res) == 0:
            raise IrmaCoreError("no probe available")
        return res
    except celery.exceptions.TimeoutError:
        raise IrmaTaskError("celery timeout on brain probe_list")


def _task_scan_progress(scanid):
    """ send a task to the brain asking for status of subtasks launched """
    try:
        task = scan_app.send_task("brain.tasks.scan_progress", args=[scanid])
        return task.get(timeout=cfg_timeout)
    except celery.exceptions.TimeoutError:
        raise IrmaTaskError("celery timeout on brain progress")


def _task_scan_cancel(scanid):
    """ send a task to the brain to cancel all remaining subtasks """
    try:
        task = scan_app.send_task("brain.tasks.scan_cancel", args=[scanid])
        return task.get(timeout=cfg_timeout)
    except celery.exceptions.TimeoutError:
        raise IrmaTaskError("celery timeout on brain scan_cancel")


# ==================
#  Public functions
# ==================

def scan_new():
    """ Create new scan

    :rtype: str
    :return: scan id
    :raise: IrmaDataBaseError
    """
    scan = ScanInfo()
    return scan.id


def scan_add(scanid, files):
    """ add file(s) to the specified scan

    :param scanid: id returned by scan_new
    :param files: dict of 'filename':str, 'data':str
    :rtype: int
    :return: int - total number of files for the scan
    :raise: IrmaDataBaseError, IrmaValueError
    """
    scan = ScanInfo(id=scanid, mode=IrmaLockMode.read)
    IrmaScanStatus.filter_status(scan.status,
                                 IrmaScanStatus.empty,
                                 IrmaScanStatus.ready)
    scan.take()
    for (name, data) in files.items():
        fobj = ScanFile()
        fobj.save(data, name)
        scan.add_file(fobj.id, name, fobj.hashvalue)
        if scan.status == IrmaScanStatus.empty:
            scan.status = IrmaScanStatus.ready
    scan.update()
    scan.release()
    return len(scan.scanfile_ids)


def scan_launch(scanid, force, probelist):
    """ launch specified scan

    :param scanid: id returned by scan_new
    :rtype: dict of 'code': int, 'msg': str [, optional 'probe_list':list]
    :return:
        on success 'probe_list' is the list of probes used for the scan
        on error 'msg' gives reason message
    :raise: IrmaDataBaseError, IrmaValueError
    """
    scan = ScanInfo(id=scanid, mode=IrmaLockMode.read)
    IrmaScanStatus.filter_status(scan.status,
                                 IrmaScanStatus.ready,
                                 IrmaScanStatus.ready)
    all_probe_list = _task_probe_list()
    scan = ScanInfo(id=scanid, mode=IrmaLockMode.write)
    if probelist is not None:
        unknown_probes = []
        for p in probelist:
            if p not in all_probe_list:
                unknown_probes.append(p)
        if len(unknown_probes) != 0:
            reason = "probe {0} unknown".format(", ".join(unknown_probes))
            raise IrmaValueError(reason)
        scan.probelist = probelist
    else:
        # all available probe
        scan.probelist = all_probe_list
    scan.update()
    scan.release()

    # launch scan via frontend task
    frontend_app.send_task("frontend.tasks.scan_launch", args=(scan.id, force))
    return scan.probelist


def scan_result(scanid):
    """ get results from files of specified scan

    :param scanid: id returned by scan_new
    :rtype: dict of sha256 value: dict of ['filename':str,
        'results':dict of [str probename: dict [results of probe]]]
    :return:
        dict of results for each hash value
    :raise: IrmaDatabaseError
    """
    # fetch results in db
    scan = ScanInfo(id=scanid, mode=IrmaLockMode.read)
    scan_res = scan.get_results()
    return scan_res


def scan_progress(scanid):
    """ get scan progress for specified scan

    :param scanid: id returned by scan_new
    :rtype: 'status': label of status [optional dict of 'total':int, 
        'finished':int, 'successful':int]
    :return:
        dict with total/finished/succesful jobs submitted by irma-brain
    :raise: IrmaDatabaseError, IrmaTaskError
    """
    scan = ScanInfo(id=scanid, mode=IrmaLockMode.read)
    if scan.status != IrmaScanStatus.launched:
        if IrmaScanStatus.is_error(scan.status):
            raise IrmaCoreError(IrmaScanStatus.label[scan.status])
        else:
            return {'status': IrmaScanStatus.label[scan.status]}
    else:
        # Else ask brain for job status
        (retcode, res) = _task_scan_progress(scanid)
        if retcode == IrmaReturnCode.success:
            if res['status'] == IrmaScanStatus.label[IrmaScanStatus.processed]:
                scan.take()
                scan.update_status(IrmaScanStatus.processed)
                scan.release()
            return res
        else:
            # else take directly error string from brain and
            # pass it to the caller
            raise IrmaTaskError(res)


def scan_cancel(scanid):
    """ cancel all remaining jobs for specified scan

    :param scanid: id returned by scan_new
    :rtype: dict of 'cancel_details': total':int, 'finished':int,
        'cancelled':int
    :return:
        informations about number of cancelled jobs by irma-brain
    :raise: IrmaDatabaseError, IrmaTaskError
    """
    scan = ScanInfo(id=scanid, mode=IrmaLockMode.read)
    if scan.status < IrmaScanStatus.uploaded:
        # If not launched answer directly
        scan.take()
        status_str = IrmaScanStatus.label[scan.status]
        scan.update_status(IrmaScanStatus.cancelled)
        scan.release()
        return None
    if scan.status != IrmaScanStatus.launched:
        # If too late answer directly
        status_str = IrmaScanStatus.label[scan.status]
        if IrmaScanStatus.is_error(scan.status):
            # let the cancel finish and keep the error status
            return None
        else:
            reason = "can not cancel scan in {0} status".format(status_str)
            raise IrmaValueError(reason)

    # Else ask brain for job cancel
    (retcode, res) = _task_scan_cancel(scanid)
    if retcode == IrmaReturnCode.success:
        if 'cancel_details' in res:
            scan = ScanInfo(id=scanid, mode=IrmaLockMode.write)
            scan.update_status(IrmaScanStatus.cancelled)
            scan.release()
            return res['cancel_details']
        elif res['status'] == IrmaScanStatus.label[IrmaScanStatus.processed]:
            # if scan is finished for the brain
            # it means we are just waiting for results
            scan = ScanInfo(id=scanid, mode=IrmaLockMode.write)
            scan.update_status(IrmaScanStatus.processed)
            scan.release()
        reason = "can not cancel scan in {0} status".format(res['status'])
        raise IrmaValueError(reason)
    else:
        raise IrmaTaskError(res)


def scan_finished(scanid):
    """ return a boolean  indicating if scan is finished
    :param scanid: id returned by scan_new
    :rtype: boolean
    :return:
        True if scan is finished
        False otherwise
    :raise: IrmaDatabaseError
    """
    scan = ScanInfo(id=scanid, mode=IrmaLockMode.read)
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
        ScanFile(sha256=sha256)
        return True
    except IrmaDatabaseResultNotFound:
        return False


def file_result(sha256):
    """ return results for file with given sha256 value

    :rtype: dict of [
            sha256 value: dict of
                'filenames':list of filename,
                'results': dict of [str probename: dict [results of probe]]]]
    :return:
        if exists returns all available scan results
        for file with given sha256 value
    :raise: IrmaDatabaseError
    """
    f = ScanFile(sha256=sha256)
    ref_res = ScanRefResults(id=f.id)
    return ref_res.get_results()


def file_infected(sha256):
    """ return antivirus score for file with given sha256 value

    :rtype: dict of ['infected':boolean,
        'nb_scan':int, 'nb_detected': int ]
    :return:
        returns detection score for
        file with given sha256 value
    :raise: IrmaDatabaseError
    """
    f = ScanFile(sha256=sha256)
    ref_res = ScanRefResults(id=f.id)
    nb_scan = nb_detected = 0
    av_results = ref_res.get_results(filter_type=["antivirus"])
    probe_res = av_results[sha256]['results']
    for res in probe_res.values():
        nb_scan += 1
        if res['result'] is not None:
            nb_detected += 1
    suspicious = False
    if nb_detected > 0:
        suspicious = True
    return {'infected': suspicious,
            'nb_detected': nb_detected,
            'nb_scan': nb_scan}
