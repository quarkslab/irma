from config.brainconfig import brain_celery
import config.probeconfig as probeconfig
from lib.irma.common.utils import success, warning, error
from lib.irma.common.objects import ScanInfo, ScanResults, ScanStatus
import uuid
import time

# Time to cache the probe list
# to avoid asking to rabbitmq
PROBELIST_CACHE_TIME = 60

cache_probelist = {'list':None, 'time':None}

def get_probelist():
    now = time.time()
    if not cache_probelist['list'] or (now - cache_probelist['time']) > PROBELIST_CACHE_TIME:
        slist = list()
        i = probeconfig.probe_celery.control.inspect()
        queues = i.active_queues()
        for infolist in queues.values():
            for info in infolist:
                if info['name'] not in slist:
                    slist.append(info['name'])
        cache_probelist['list'] = slist
        cache_probelist['time'] = now
    return cache_probelist['list']

@brain_celery.task()
def probe_list():
    return success(get_probelist())

@brain_celery.task(ignore_result=True)
def scan(scanid, oids, probelist, force):
    scaninfo = ScanInfo(_id=scanid)
    scaninfo.save()

    all_probe = get_probelist()
    print "Received probelist %r" % probelist
    if probelist:
        # check if probe exists
        for x in probelist:
            if x not in all_probe:
                print x + " not in " + "-".join(all_probe)
                raise 'Unknown probe :' + x
        scaninfo.probelist = probelist
    else:
        scaninfo.probelist = all_probe

    jobs_list = []
    print "Scan received with %d files and analysis (%s) and force %r" % (len(oids), scaninfo.probelist, force)
    for (oid, oid_info) in oids.items():
        scaninfo.oids[oid] = oid_info['name']
        for probe in scaninfo.probelist:
            if oid_info['new'] or force:
                # create one subtask per oid to scan per antivirus queue
                jobs_list.append(probeconfig.probe_celery.send_task("probe.probetasks.probe_scan", args=(scanid, oid), queue=probe))
                print 'Append new job to %s queue' % probe
            else:
                # TODO update new filename for known oid if different
                # check if resuls for all probe is already there else launch specific scan
                scanresult = ScanResults(_id=oid)
                if probe not in scanresult.results.keys():
                    jobs_list.append(probeconfig.probe_celery.send_task("probe.probetasks.probe_scan", args=(scanid, oid), queue=probe))
                    print 'Append add job to %s queue' % probe

    if len(jobs_list) != 0:
        # Build a result set with all job AsyncResult for progress/cancel operations
        groupid = str(uuid.uuid4())
        groupres = probeconfig.probe_celery.GroupResult(id=groupid, results=jobs_list)

        # keep the groupresult object for task status/cancel
        groupres.save()
        scaninfo.status = ScanStatus.launched
        scaninfo.taskid = groupid
    else:
        scaninfo.status = ScanStatus.finished
    return "%d jobs launched" % len(jobs_list)

@brain_celery.task(ignore_result=True)
def scan_finished(scanid):
    s = ScanInfo(_id=scanid)
    s.status = ScanStatus.finished
    return

@brain_celery.task()
def scan_progress(scanid):
    s = ScanInfo(_id=scanid)
    if s.status == ScanStatus.init:
        return warning("task not launched")
    elif s.status == ScanStatus.launched:
        if not s.taskid:
            return error("task_id not set")
        job = probeconfig.probe_celery.GroupResult.restore(s.taskid)
        if not job:
            return error("not a valid taskid")
        else:
            nbcompleted = nbsuccessful = 0
            for j in job:
                if j.ready(): nbcompleted += 1
                if j.successful(): nbsuccessful += 1
            if nbcompleted == len(job):
                s.status = ScanStatus.finished
            return success({"total":len(job), "finished":nbcompleted, "successful":nbsuccessful})
    elif s.status == ScanStatus.finished:
        return warning("finished")
    elif s.status == ScanStatus.cancelling:
        return warning("cancelling")
    elif s.status == ScanStatus.cancelled:
        return warning("cancelled")
    return error("unknown status %d" % s.status)

@brain_celery.task()
def scan_cancel(scanid):
    s = ScanInfo(_id=scanid)
    if s.status == ScanStatus.init:
        return error("task not launched")
    elif s.status == ScanStatus.launched:
        job = probeconfig.probe_celery.GroupResult.restore(s.taskid)
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
            s.status = ScanStatus.cancelled
            return success({"total":len(job), "finished":nbcompleted, "cancelled":nbcancelled})
    elif s.status == ScanStatus.finished:
        return warning("finished")
    elif s.status == ScanStatus.cancelled:
        return warning("cancelled")
    return error("unknown status %d" % s.status)

@brain_celery.task()
def scan_result(scanid):
    s = ScanInfo(_id=scanid)
    return success(s.get_results())
