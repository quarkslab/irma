import celery
from brain import brainstorage
import config
from lib.irma.common.utils import IRMA_RETCODE_OK, IRMA_RETCODE_WARNING, IRMA_RETCODE_ERROR
from config.dbconfig import SCAN_STATUS_LAUNCHED, SCAN_STATUS_FINISHED, SCAN_STATUS_CANCELLED, SCAN_STATUS_INIT, SCAN_STATUS_CANCELLING
import uuid

celery_brain = celery.Celery('braintasks')
celery_brain.config_from_object('config.brainconfig')
bstorage = brainstorage.BrainStorage()

sonde_celery = celery.Celery('sondetasks')
sonde_celery.config_from_object('config.sondeconfig')

def success(info):
    return (IRMA_RETCODE_OK, info)

def warning(info):
    return (IRMA_RETCODE_WARNING, info)

def error(info):
    return (IRMA_RETCODE_ERROR, info)


@celery_brain.task(ignore_result=True)
def scan(scanid, oids):
    bstorage.update_scan_record(scanid, {'status':SCAN_STATUS_INIT, 'oids': oids, 'avlist':[]})

    avlist = ['clamav', 'kaspersky']
    res = []
    for (oid, oid_info) in oids.items():
        for av in avlist:
            if oid_info['new']:
                # create one subtask per oid to scan per antivirus queue
                res.append(sonde_celery.send_task("sonde.sondetasks.sonde_scan", args=(scanid, oid), queue=av))
            else:
                # TODO update new filename for known oid if different
                # TODO check if resuls for all av is present else launch specific scan
                print "oid %s (%s) already scanned not launching" % (oid, oid_info['name'])

    if len(res) != 0:
        # Build a result set with all job AsyncResult for progress/cancel operations
        groupid = str(uuid.uuid4())
        groupres = sonde_celery.GroupResult(id=groupid, results=res)

        # keep the groupresult object for task status/cancel
        groupres.save()
        bstorage.update_scan_record(scanid, {'status':SCAN_STATUS_LAUNCHED, 'taskid':groupid , 'avlist':avlist})
    else:
        bstorage.update_scan_record(scanid, {'status':SCAN_STATUS_FINISHED, 'taskid':None , 'avlist':avlist})
    return

@celery_brain.task(ignore_result=True)
def scan_finished(scanid):
    bstorage.update_scan_record(scanid, {'status':SCAN_STATUS_FINISHED})
    return

@celery_brain.task()
def scan_progress(scanid):
    status = bstorage.get_scan_status(scanid)
    if status == SCAN_STATUS_INIT:
        return warning("task not launched")
    elif status == SCAN_STATUS_LAUNCHED:
        task_id = bstorage.get_scan_taskid(scanid)
        if not task_id:
            return error("task_id not set")
        job = sonde_celery.GroupResult.restore(task_id)
        if not job:
            return error("not a valid taskid")
        else:
            nbcompleted = nbsuccessful = 0
            for j in job:
                if j.ready(): nbcompleted += 1
                if j.successful(): nbsuccessful += 1
            if nbsuccessful == len(job):
                bstorage.update_scan_record(scanid, {'status':SCAN_STATUS_FINISHED})
            return success({"total":len(job), "finished":nbcompleted, "successful":nbsuccessful})
    elif status == SCAN_STATUS_FINISHED:
        return warning("finished")
    elif status == SCAN_STATUS_CANCELLING:
        return warning("cancelling")
    elif status == SCAN_STATUS_CANCELLED:
        return warning("cancelled")
    return error("unknown status %d" % status)


@celery_brain.task()
def scan_cancel(scanid):
    bstorage.update_scan_record(scanid, {'status':SCAN_STATUS_CANCELLING})

    status = bstorage.get_scan_status(scanid)
    if status == SCAN_STATUS_INIT:
        return error("task not launched")
    elif status == SCAN_STATUS_LAUNCHED:
        task_id = bstorage.get_scan_taskid(scanid)
        job = sonde_celery.GroupResult.restore(task_id)
        if not job:
            return error("not a valid taskid")
        else:
            nbcompleted = nbcancelled = 0
            for j in job:
                if j.ready():
                    nbcompleted += 1
                else:
                    j.revoke(terminate=True)
                    nbcancelled += 1
            bstorage.update_scan_record(scanid, {'status':SCAN_STATUS_CANCELLED})
            return success({"total":len(job), "finished":nbcompleted, "cancelled":nbcancelled})
    elif status == SCAN_STATUS_FINISHED:
        return warning("finished")
    elif status == SCAN_STATUS_CANCELLED:
        return warning("cancelled")
    return error("unknown status %d" % status)

@celery_brain.task()
def scan_result(scanid):
    oids = bstorage.get_scan_fileoid(scanid)
    res = {}
    for (oid, info) in oids.items():
        res[info['name']] = bstorage.get_result(oid)
    return success(res)



