import celery
import config.parser as config
from frontend.objects import ScanInfo, ScanFile, ScanResults
from lib.irma.common.utils import IrmaReturnCode, IrmaScanStatus, IrmaLockMode

# ______________________________________________________________________________ FRONTEND Exceptions

class IrmaFrontendWarning(Exception):
    pass

class IrmaFrontendError(Exception):
    pass

# ______________________________________________________________________________ Task functions

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

# ______________________________________________________________________________ Public functions

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
    oids = {}
    for (name, data) in files.items():
        fobj = ScanFile()
        fobj.save(data, name)
        # fetch probe results already present
        probedone = ScanResults.init_id(fobj.id).probelist
        oids[fobj.id] = {'name':name, 'probedone':probedone}
    scan = ScanInfo(id=scanid, mode=IrmaLockMode.write)
    scan.oids = oids
    scan.update()
    scan.release()
    return len(scan.oids)

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
        scan.probelist = probelist
    else:
        # all available probe
        scan.probelist = all_probe_list
    scan.update()
    scan.release()

    # launch scan via frontend task
    frontend_app.send_task("frontend.tasks.scan_launch", args=(scan.id, force))
    return scan.probelist

def scan_results(scanid):
    """ get all results from files of specified scan 
    
    :param scanid: id returned by scan_new
    :rtype: dict of sha256 value: dict of ['filename':str, 'results':dict of [str probename: dict [results of probe]]]
    :return: 
        dict of results for each hash value
    :raise: IrmaDatabaseError
    """
    # fetch results in db
    scan = ScanInfo(id=scanid, mode=IrmaLockMode.read)
    return scan.get_results()

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
        # if scan is processed for the brain, it means all probes jobs are completes
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
    :rtype: dict of 'cancel_details': total':int, 'finished':int, 'cancelled':int
    :return: 
        informations about number of cancelled jobs by irma-brain
    :raise: IrmaDatabaseError, IrmaFrontendWarning, IrmaFrontendError
    """
    scan = ScanInfo(id=scanid, mode=IrmaLockMode.read)
    if scan.status != IrmaScanStatus.launched:
        # If not launched answer directly
        # Else ask brain for job status

        raise IrmaFrontendWarning(IrmaScanStatus.label[scan.status])
    (status, res) = _task_scan_cancel(scanid)
    if status == IrmaReturnCode.success:
        scan = ScanInfo(id=scanid, mode=IrmaLockMode.write)
        scan.update_status(IrmaScanStatus.cancelled)
        scan.release()
        return res
    elif status == IrmaReturnCode.warning:
        # if scan is finished for the brain, it means we are just waiting for results
        if res == IrmaScanStatus.processed:
            scan = ScanInfo(id=scanid, mode=IrmaLockMode.write)
            scan.update_status(IrmaScanStatus.processed)
            scan.release()
        raise IrmaFrontendWarning(IrmaScanStatus.label[res])
    else:
        raise IrmaFrontendError(res)

def probe_list():
    """ get active probe list
    
    :rtype: list of str
    :return: 
        list of probes names
    :raise: IrmaFrontendWarning, IrmaFrontendError
    """
    return _task_probe_list()

