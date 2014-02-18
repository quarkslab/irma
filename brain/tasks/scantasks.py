from lib.irma.common.utils import IrmaTaskReturn
import uuid
import time
from celery import Celery
import config
from brain.objects import User, Scan
from lib.irma.database.sqlhandler import SQLDatabase

# Time to cache the probe list
# to avoid asking to rabbitmq
PROBELIST_CACHE_TIME = 60
cache_probelist = {'list':None, 'time':None}

scan_app = Celery('scantasks')
config.conf_brain_celery(scan_app)

probe_app = Celery('probetasks')
config.conf_probe_celery(probe_app)

results_app = Celery('restasks')
config.conf_results_celery(results_app)

def route(sig):
    options = sig.app.amqp.router.route(
        sig.options, sig.task, sig.args, sig.kwargs,
    )
    try:
        queue = options.pop('queue')
    except KeyError:
        pass
    else:
        options.update(exchange=queue.exchange.name,
                       routing_key=queue.routing_key)
    sig.set(**options)
    return sig


def get_probelist():
    now = time.time()
    if not cache_probelist['list'] or (now - cache_probelist['time']) > PROBELIST_CACHE_TIME:
        slist = list()
        i = probe_app.control.inspect()
        queues = i.active_queues()
        if queues:
            for infolist in queues.values():
                for info in infolist:
                    if info['name'] not in slist and info['name'] != config.brain_config['broker_probe'].queue:
                        slist.append(info['name'])
        cache_probelist['list'] = slist
        cache_probelist['time'] = now
    return cache_probelist['list']

@scan_app.task()
def probe_list():
    return IrmaTaskReturn.success(get_probelist())

@scan_app.task(ignore_result=True)
def scan(scanid, scan_request):
    available_probelist = get_probelist()
    jobs_list = []
    for (filename, probelist) in scan_request:
        if probelist:
            for p in probelist:
                # check if probe exists
                if p not in available_probelist:
                    raise "Unknown probe {0}".format(p)
        else:
            probelist = available_probelist

        # create one subtask per oid to scan per antivirus queue
        for probe in probelist:
            callback_signature = route(results_app.signature("brain.tasks.restasks.scan_result", ("frontend1", scanid, filename, probe)))
            jobs_list.append(probe_app.send_task("probe.probetasks.probe_scan", args=("frontend1", scanid, filename), queue=probe, link=callback_signature))

    if len(jobs_list) != 0:
        # Build a result set with all job AsyncResult for progress/cancel operations
        groupid = str(uuid.uuid4())
        groupres = probe_app.GroupResult(id=groupid, results=jobs_list)
        # keep the groupresult object for task status/cancel
        groupres.save()
        print "connect to {0} + {1}".format(config.brain_config['sql_brain'].engine, config.brain_config['sql_brain'].dbname)
        sql = SQLDatabase(config.brain_config['sql_brain'].engine + config.brain_config['sql_brain'].dbname)
        user = sql.find(User, rmqvhost="mqfrontend")[0]
        print user
        scan = Scan(scanid=scanid, taskid=groupid, nbfiles=len(jobs_list), status=Scan.status_launched)
        scan.user_id = user.id
        sql.add(scan)
        sql.commit()
        print scan
    print "%d files receives / %d active probe / %d probe used / %d jobs launched" % (len(scan_request), len(available_probelist), len(probelist), len(jobs_list))
    return

@scan_app.task(ignore_result=True)
def scan_finished(scanid):
    """
    s = ScanInfo(_id=scanid)
    s.status = ScanStatus.finished
    """
    return

@scan_app.task()
def scan_progress(scanid):
    """
    s = ScanInfo(_id=scanid)
    if s.status == ScanStatus.init:
        return IrmaTaskReturn.warning("task not launched")
    elif s.status == ScanStatus.launched:
        if not s.taskid:
            return IrmaTaskReturn.error("task_id not set")
        job = probe_app.GroupResult.restore(s.taskid)
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

@scan_app.task()
def scan_cancel(scanid):
    """
    s = ScanInfo(_id=scanid)
    if s.status == ScanStatus.init:
        return IrmaTaskReturn.error("task not launched")
    elif s.status == ScanStatus.launched:
        job = probe_app.GroupResult.restore(s.taskid)
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

