from lib.irma.common.utils import IrmaTaskReturn
import uuid
import time
from celery import Celery
import config

# Time to cache the probe list
# to avoid asking to rabbitmq
PROBELIST_CACHE_TIME = 60
cache_probelist = {'list':None, 'time':None}

brain_celery = Celery('braintasks')
config.conf_brain_celery(brain_celery)

probe_celery = Celery('probetasks')
config.conf_probe_celery(probe_celery)

def get_probelist():
    now = time.time()
    if not cache_probelist['list'] or (now - cache_probelist['time']) > PROBELIST_CACHE_TIME:
        slist = list()
        i = probe_celery.control.inspect()
        queues = i.active_queues()
        if queues:
            for infolist in queues.values():
                for info in infolist:
                    if info['name'] not in slist:
                        slist.append(info['name'])
        cache_probelist['list'] = slist
        cache_probelist['time'] = now
    return cache_probelist['list']

@brain_celery.task()
def probe_list():
    return IrmaTaskReturn.success(get_probelist())

@brain_celery.task(ignore_result=True)
def scan(scanid, oids, probelist):
    all_probe = get_probelist()
    if probelist:
        # check if probe exists
        for x in probelist:
            if x not in all_probe:
                raise 'Unknown probe :' + x
    else:
        probelist = all_probe

    jobs_list = []
    for (oid, oid_info) in oids.items():
        for probe in probelist:
            # create one subtask per oid to scan per antivirus queue
            jobs_list.append(probe_celery.send_task("probe.probetasks.probe_scan", args=(scanid, oid), queue=probe))

    if len(jobs_list) != 0:
        # Build a result set with all job AsyncResult for progress/cancel operations
        groupid = str(uuid.uuid4())
        groupres = probe_celery.GroupResult(id=groupid, results=jobs_list)

        # keep the groupresult object for task status/cancel
        groupres.save()
        # TODO keep info scanid <-> taskid
        # scaninfo.status = ScanStatus.launched
        # scaninfo.taskid = groupid
    print "%d files receives / %d active probe / %d probe used / %d jobs launched" % (len(oids), len(all_probe), len(probelist), len(jobs_list))
    return

@brain_celery.task(ignore_result=True)
def scan_finished(scanid):
    """
    s = ScanInfo(_id=scanid)
    s.status = ScanStatus.finished
    """
    return

@brain_celery.task()
def scan_progress(scanid):
    """
    s = ScanInfo(_id=scanid)
    if s.status == ScanStatus.init:
        return IrmaTaskReturn.warning("task not launched")
    elif s.status == ScanStatus.launched:
        if not s.taskid:
            return IrmaTaskReturn.error("task_id not set")
        job = probe_celery.GroupResult.restore(s.taskid)
        if not job:
            return IrmaTaskReturn.error("not a valid taskid")
        else:
            nbcompleted = nbsuccessful = 0
            for j in job:
                if j.ready(): nbcompleted += 1
                if j.successful(): nbsuccessful += 1
            if nbcompleted == len(job):
                s.status = ScanStatus.finished
            return IrmaTaskReturn.success({"total":len(job), "finished":nbcompleted, "successful":nbsuccessful})
    elif s.status == ScanStatus.finished:
        return IrmaTaskReturn.warning("finished")
    elif s.status == ScanStatus.cancelling:
        return IrmaTaskReturn.warning("cancelling")
    elif s.status == ScanStatus.cancelled:
        return IrmaTaskReturn.warning("cancelled")
    """
    return IrmaTaskReturn.error("unknown")

@brain_celery.task()
def scan_cancel(scanid):
    """
    s = ScanInfo(_id=scanid)
    if s.status == ScanStatus.init:
        return IrmaTaskReturn.error("task not launched")
    elif s.status == ScanStatus.launched:
        job = probe_celery.GroupResult.restore(s.taskid)
        if not job:
            return IrmaTaskReturn.error("not a valid taskid")
        else:
            nbcompleted = nbcancelled = 0
            for j in job:
                if j.ready():
                    nbcompleted += 1
                else:
                    j.revoke(terminate=True)
                    nbcancelled += 1
            s.status = ScanStatus.cancelled
            return IrmaTaskReturn.success({"total":len(job), "finished":nbcompleted, "cancelled":nbcancelled})
    elif s.status == ScanStatus.finished:
        return IrmaTaskReturn.warning("finished")
    elif s.status == ScanStatus.cancelled:
        return IrmaTaskReturn.warning("cancelled")
        """
    return IrmaTaskReturn.error("unknown")

@brain_celery.task()
def scan_result(scanid):
    """
    s = ScanInfo(_id=scanid)
    return IrmaTaskReturn.success(s.get_results())
    """
    return IrmaTaskReturn.error("unknown")