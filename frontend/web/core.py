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
from frontend.nosqlobjects import ScanInfo, ScanFile, ScanRefResults
from lib.irma.common.utils import IrmaReturnCode, IrmaScanStatus, IrmaLockMode
from lib.irma.common.exceptions import IrmaDatabaseError, \
    IrmaDatabaseResultNotFound
from frontend.format import IrmaProbeType


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
    :raise: IrmaDataBaseError
    """
    scan = ScanInfo(id=scanid, mode=IrmaLockMode.read)
    if scan.status != IrmaScanStatus.created:
        # Can not add file to scan launched
        raise IrmaFrontendWarning(IrmaScanStatus.label[scan.status])
    scan.take()
    for (name, data) in files.items():
        fobj = ScanFile()
        fobj.save(data, name)
        scan.add_file(fobj.id, name, fobj.hashvalue)
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
    :raise: IrmaDataBaseError, IrmaFrontendError
    """
    scan = ScanInfo(id=scanid, mode=IrmaLockMode.read)
    if scan.status != IrmaScanStatus.created:
        # Can not launch scan with other status
        raise IrmaFrontendWarning(IrmaScanStatus.label[scan.status])
    all_probe_list = _task_probe_list()
    if len(all_probe_list) == 0:
        scan = ScanInfo(id=scanid, mode=IrmaLockMode.write)
        scan.update_status(IrmaScanStatus.finished)
        scan.release()
        raise IrmaFrontendError("No probe available")

    scan = ScanInfo(id=scanid, mode=IrmaLockMode.write)
    if probelist is not None:
        unknown_probes = []
        for p in probelist:
            if p not in all_probe_list:
                unknown_probes.append(p)
        if len(unknown_probes) != 0:
            reason = "Probe {0} unknown".format(", ".join(unknown_probes))
            scan.update_status(IrmaScanStatus.cancelled)
            scan.release()
            raise IrmaFrontendError(reason)
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
    :rtype: dict of 'total':int, 'finished':int, 'successful':int
    :return:
        dict with total/finished/succesful jobs submitted by irma-brain
    :raise: IrmaDatabaseError, IrmaFrontendWarning, IrmaFrontendError
    """
    scan = ScanInfo(id=scanid, mode=IrmaLockMode.read)
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
            scan = ScanInfo(id=scanid, mode=IrmaLockMode.write)
            scan.update_status(IrmaScanStatus.processed)
            scan.release()
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
    scan = ScanInfo(id=scanid, mode=IrmaLockMode.read)
    if scan.status != IrmaScanStatus.launched:
        # If not launched answer directly
        # Else ask brain for job status
        scan.take()
        scan.update_status(IrmaScanStatus.cancelled)
        scan.release()
        raise IrmaFrontendWarning(IrmaScanStatus.label[scan.status])

    (status, res) = _task_scan_cancel(scanid)
    if status == IrmaReturnCode.success:
        scan = ScanInfo(id=scanid, mode=IrmaLockMode.write)
        scan.update_status(IrmaScanStatus.cancelled)
        scan.release()
        return res
    elif status == IrmaReturnCode.warning:
        # if scan is finished for the brain
        # it means we are just waiting for results
        if res == IrmaScanStatus.processed:
            scan = ScanInfo(id=scanid, mode=IrmaLockMode.write)
            scan.update_status(IrmaScanStatus.processed)
            scan.release()
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
    except IrmaDatabaseError as e:
        raise IrmaFrontendError(str(e))


def file_result(sha256):
    """ return results for file with given sha256 value

    :rtype: dict of [
            sha256 value: dict of
                'filenames':list of filename,
                'results': dict of [str probename: dict [results of probe]]]]
    :return:
        if exists returns all available scan results
        for file with given sha256 value
    :raise: IrmaFrontendError
    """
    try:
        f = ScanFile(sha256=sha256)
        ref_res = ScanRefResults(id=f.id)
        return ref_res.get_results()
    except IrmaDatabaseError as e:
        raise IrmaFrontendWarning(str(e))


def file_infected(sha256):
    """ return antivirus score for file with given sha256 value

    :rtype: dict of ['infected':boolean,
        'nb_scan':int, 'nb_detected': int ]
    :return:
        returns detection score for
        file with given sha256 value
    :raise: IrmaFrontendError
    """
    try:
        f = ScanFile(sha256=sha256)
        ref_res = ScanRefResults(id=f.id)
        nb_scan = nb_detected = 0
        av_results = ref_res.get_results(filter_type=[IrmaProbeType.antivirus])
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
    except IrmaDatabaseError as e:
        raise IrmaFrontendWarning(str(e))
