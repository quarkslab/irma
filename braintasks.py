import celery
import config
from lib.irma.common.utils import IRMA_RETCODE_OK, IRMA_RETCODE_WARNING, IRMA_RETCODE_ERROR
from lib.irma.database.objects import ScanInfo, ScanResults
from config.dbconfig import SCAN_STATUS_LAUNCHED, SCAN_STATUS_FINISHED, SCAN_STATUS_CANCELLED, SCAN_STATUS_INIT, SCAN_STATUS_CANCELLING
import uuid

celery_brain = celery.Celery('braintasks')
celery_brain.config_from_object('config.brainconfig')

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
    s = ScanInfo(_id=scanid)
    s.status = SCAN_STATUS_INIT
    for (oid, oid_info) in oids:
        s.oids.append(oid)
    s.save()

    avlist = ['clamav', 'kaspersky']
    s.avlist = avlist
    res = []
    for (oid, oid_info) in oids.items():
        for av in avlist:
            if oid_info['new']:
                # create one subtask per oid to scan per antivirus queue
                res.append(sonde_celery.send_task("sonde.sondetasks.sonde_scan", args=(scanid, oid), queue=av))
            else:
                # TODO update new filename for known oid if different
                # check if resuls for all av is present else launch specific scan
                r = ScanResults(_id=oid)
                for av in avlist:
                    if av not in r.results.keys():
                        res.append(sonde_celery.send_task("sonde.sondetasks.sonde_scan", args=(scanid, oid), queue=av))
                    else:
                        print "oid %s (%s) already scanned by %s not launching" % (oid, oid_info['name'], av)

    if len(res) != 0:
        # Build a result set with all job AsyncResult for progress/cancel operations
        groupid = str(uuid.uuid4())
        groupres = sonde_celery.GroupResult(id=groupid, results=res)

        # keep the groupresult object for task status/cancel
        groupres.save()
        s.status = SCAN_STATUS_LAUNCHED
        s.taskid = groupid
    else:
        s.status = SCAN_STATUS_FINISHED
    return

@celery_brain.task(ignore_result=True)
def scan_finished(scanid):
    s = ScanInfo(_id=scanid)
    s.status = SCAN_STATUS_FINISHED
    return

@celery_brain.task()
def scan_progress(scanid):
    s = ScanInfo(_id=scanid)
    if s.status == SCAN_STATUS_INIT:
        return warning("task not launched")
    elif s.status == SCAN_STATUS_LAUNCHED:
        if not s.taskid:
            return error("task_id not set")
        job = sonde_celery.GroupResult.restore(s.taskid)
        if not job:
            return error("not a valid taskid")
        else:
            nbcompleted = nbsuccessful = 0
            for j in job:
                if j.ready(): nbcompleted += 1
                if j.successful(): nbsuccessful += 1
            if nbcompleted == len(job):
                s.status = SCAN_STATUS_FINISHED
            return success({"total":len(job), "finished":nbcompleted, "successful":nbsuccessful})
    elif s.status == SCAN_STATUS_FINISHED:
        return warning("finished")
    elif s.status == SCAN_STATUS_CANCELLING:
        return warning("cancelling")
    elif s.status == SCAN_STATUS_CANCELLED:
        return warning("cancelled")
    return error("unknown status %d" % s.status)

@celery_brain.task()
def scan_cancel(scanid):
    s = ScanInfo(_id=scanid)

    if s.status == SCAN_STATUS_INIT:
        return error("task not launched")
    elif s.status == SCAN_STATUS_LAUNCHED:
        job = sonde_celery.GroupResult.restore(s.taskid)
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
            s.status = SCAN_STATUS_CANCELLED
            return success({"total":len(job), "finished":nbcompleted, "cancelled":nbcancelled})
    elif s.status == SCAN_STATUS_FINISHED:
        return warning("finished")
    elif s.status == SCAN_STATUS_CANCELLED:
        return warning("cancelled")
    return error("unknown status %d" % s.status)

@celery_brain.task()
def scan_result(scanid):
    s = ScanInfo(_id=scanid)
    res = {}
    for (oid, info) in s.oids.items():
        r = ScanResults(_id=oid)
        res[info['name']] = r.results
    return success(res)
