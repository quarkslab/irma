from config.brainconfig import brain_celery
from config.sondeconfig import sonde_celery
from lib.irma.common.utils import IRMA_RETCODE_OK, IRMA_RETCODE_WARNING, IRMA_RETCODE_ERROR
from lib.irma.database.objects import ScanInfo, ScanResults
from config.dbconfig import SCAN_STATUS_LAUNCHED, SCAN_STATUS_FINISHED, SCAN_STATUS_CANCELLED, SCAN_STATUS_INIT, SCAN_STATUS_CANCELLING
import uuid
import time

cache_sonde = {'list':None, 'time':None}

def get_sondelist():
    now = time.time()
    if not cache_sonde['list'] or (now - cache_sonde['time']) > 60:
        slist = list()
        i = sonde_celery.control.inspect()
        queues = i.active_queues()
        for infolist in queues.values():
            for info in infolist:
                if info['name'] not in slist:
                    slist.append(info['name'])
        cache_sonde['list'] = slist
        cache_sonde['time'] = now
    return cache_sonde['list']

def success(info):
    return (IRMA_RETCODE_OK, info)

def warning(info):
    return (IRMA_RETCODE_WARNING, info)

def error(info):
    return (IRMA_RETCODE_ERROR, info)

@brain_celery.task()
def sonde_list():
    return success(get_sondelist())

@brain_celery.task(ignore_result=True)
def scan(scanid, oids, sondelist, force):
    # TODO remove empty dict hack for oids init
    s = ScanInfo(_id=scanid)
    s.save()
    if sondelist:
        s.sondelist = sondelist
    else:
        s.sondelist = get_sondelist()
    res = []
    for (oid, oid_info) in oids.items():
        s.oids[oid] = oid_info['name']
        for av in s.sondelist:
            if oid_info['new'] or force:
                # create one subtask per oid to scan per antivirus queue
                res.append(sonde_celery.send_task("sonde.sondetasks.sonde_scan", args=(scanid, oid), queue=av))
            else:
                # TODO update new filename for known oid if different
                # check if resuls for all av is present else launch specific scan
                r = ScanResults(_id=oid)
                if av not in r.results.keys():
                    res.append(sonde_celery.send_task("sonde.sondetasks.sonde_scan", args=(scanid, oid), queue=av))

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
    return "%d jobs launched" % len(res)

@brain_celery.task(ignore_result=True)
def scan_finished(scanid):
    s = ScanInfo(_id=scanid)
    s.status = SCAN_STATUS_FINISHED
    return

@brain_celery.task()
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

@brain_celery.task()
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

@brain_celery.task()
def scan_result(scanid):
    s = ScanInfo(_id=scanid)
    res = {}
    for (oid, name) in s.oids.items():
        r = ScanResults(_id=oid)
        res[name] = r.results
    return success(res)
