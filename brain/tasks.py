import uuid
import time
from celery import Celery
import config
from datetime import datetime, timedelta
from brain.objects import User, Scan
from lib.irma.common.utils import IrmaTaskReturn, IrmaScanStatus
from lib.irma.common.exceptions import IrmaTaskError, IrmaDatabaseError
from lib.irma.database.sqlhandler import SQLDatabase
from lib.irma.ftp.handler import FtpTls

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

frontend_app = Celery('frontendtasks')
config.conf_frontend_celery(frontend_app)

# ______________________________________________________________________________ SQL Helpers


def get_quota(sql, user):
    if user.quota == 0:
        # quota=0 means quota disabled
        quota = None
    else:
        # Quota are set per 24 hours
        delta = timedelta(hours=24)
        quota = user.quota - sql.sum(Scan.nbfiles, "user_id={0} and date >= '{1}'".format(user.id, datetime.now() - delta))
    return quota

def get_groupresult(taskid):
    if not taskid:
        raise IrmaTaskError("task_id not set")
    gr = probe_app.GroupResult.restore(taskid)
    if not gr:
        raise IrmaTaskError("not a valid taskid")
    return gr

# ______________________________________________________________________________ Celery Helpers

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

# ______________________________________________________________________________ Tasks Helpers

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

def flush_dir(frontend, scanid):
    conf_ftp = config.brain_config['ftp_brain']
    with FtpTls(conf_ftp.host, conf_ftp.port, conf_ftp.username, conf_ftp.password) as ftps:
        ftps.deletepath("{0}/{1}".format(frontend, scanid), deleteParent=True)

# ______________________________________________________________________________ Tasks Declaration

@scan_app.task()
def probe_list():
    return IrmaTaskReturn.success(get_probelist())

@scan_app.task(ignore_result=True)
def scan(scanid, scan_request):
    sql = SQLDatabase(config.brain_config['sql_brain'].engine + config.brain_config['sql_brain'].dbname)
    available_probelist = get_probelist()
    jobs_list = []
    # FIXME get rmq_vhost
    rmqvhost = "mqfrontend"
    try:
        user = sql.one_by(User, rmqvhost=rmqvhost)
        quota = get_quota(sql, user)
        if quota is not None:
            print "Found user {0} quota remaining {1}/{2}".format(user.name, quota, user.quota)
        else:
            print "Found user {0} quota disabled".format(user.name)
    except IrmaTaskError as e:
        return IrmaTaskReturn.error("{0}".format(e))

    for (filename, probelist) in scan_request:
        if probelist is None:
            return IrmaTaskReturn.error("Empty probe list")
        # first check probelist
        for p in probelist:
            # check if probe exists
            if p not in available_probelist:
                return IrmaTaskReturn.error("Unknown probe {0}".format(p))

        # Now, create one subtask per file to scan per probe according to quota
        for probe in probelist:
            if quota is not None and quota <= 0:
                break;
            if quota:
                quota -= 1
            callback_signature = route(results_app.signature("brain.tasks.scan_result", ("frontend1", scanid, filename, probe)))
            jobs_list.append(probe_app.send_task("probe.tasks.probe_scan", args=("frontend1", scanid, filename), queue=probe, link=callback_signature))

    if len(jobs_list) != 0:
        # Build a result set with all job AsyncResult for progress/cancel operations
        groupid = str(uuid.uuid4())
        groupres = probe_app.GroupResult(id=groupid, results=jobs_list)
        # keep the groupresult object for task status/cancel
        groupres.save()

        scan = Scan(scanid=scanid, taskid=groupid, nbfiles=len(jobs_list), status=IrmaScanStatus.launched, user_id=user.id, date=datetime.now())
        sql.add(scan)
    print "%d files receives / %d active probe / %d probe used / %d jobs launched" % (len(scan_request), len(available_probelist), len(probelist), len(jobs_list))
    return

@scan_app.task()
def scan_progress(scanid):
    try:
        sql = SQLDatabase(config.brain_config['sql_brain'].engine + config.brain_config['sql_brain'].dbname)
    except Exception as e:
        return IrmaTaskReturn.error("Brain SQL: {0}".format(e))
    # FIXME get rmq_vhost
    rmqvhost = "mqfrontend"
    try:
        user = sql.one_by(User, rmqvhost=rmqvhost)
    except Exception as e:
        return IrmaTaskReturn.error("User: {0}".format(e))
    try:
        scan = sql.one_by(Scan, scanid=scanid, user_id=user.id)
    except Exception as e:
        return IrmaTaskReturn.warning(IrmaScanStatus.created)
    if scan.status == IrmaScanStatus.launched:
        if not scan.taskid:
            return IrmaTaskReturn.error("task_id not set")
        gr = get_groupresult(scan.taskid)
        nbcompleted = nbsuccessful = 0
        for j in gr:
            if j.ready(): nbcompleted += 1
            if j.successful(): nbsuccessful += 1
        return IrmaTaskReturn.success({"total":len(gr), "finished":nbcompleted, "successful":nbsuccessful})
    else:
        return IrmaTaskReturn.warning(scan.status)

@scan_app.task()
def scan_cancel(scanid):
    try:
        sql = SQLDatabase(config.brain_config['sql_brain'].engine + config.brain_config['sql_brain'].dbname)
        # FIXME get rmq_vhost
        rmqvhost = "mqfrontend"
        try:
            user = sql.one_by(User, rmqvhost=rmqvhost)
        except IrmaDatabaseError as e:
            return IrmaTaskReturn.error("User: {0}".format(e))
        try:
            scan = sql.one_by(Scan, scanid=scanid, user_id=user.id)
        except IrmaDatabaseError:
            return IrmaTaskReturn.warning(IrmaScanStatus.created)
        if scan.status == IrmaScanStatus.launched:
            scan.status = IrmaScanStatus.cancelling
            # commit as soon as possible to avoid cancelling again
            sql.commit()
            gr = get_groupresult(scan.taskid)
            nbcompleted = nbcancelled = 0
            # iterate over jobs in groupresult
            for j in gr:
                if j.ready():
                    nbcompleted += 1
                else:
                    j.revoke(terminate=True)
                    nbcancelled += 1
            scan.status = IrmaScanStatus.cancelled
            return IrmaTaskReturn.success({"total":len(gr), "finished":nbcompleted, "cancelled":nbcancelled})
        else:
            return IrmaTaskReturn.warning(scan.status)
    except IrmaTaskError as e:
        return IrmaTaskReturn.error("{0}".format(e))

@results_app.task(ignore_result=True)
def scan_result(result, frontend, scanid, filename, probe):
    try:
        sql = SQLDatabase(config.brain_config['sql_brain'].engine + config.brain_config['sql_brain'].dbname)
        # FIXME get rmq_vhost
        rmqvhost = "mqfrontend"
        user = sql.one_by(User, rmqvhost=rmqvhost)
        scan = sql.one_by(Scan, scanid=scanid, user_id=user.id)
        gr = get_groupresult(scan.taskid)
        nbtotal = len(gr)
        nbcompleted = nbsuccessful = 0
        for j in gr:
            if j.ready(): nbcompleted += 1
            if j.successful(): nbsuccessful += 1
        if nbtotal == nbcompleted:
            scan.status = IrmaScanStatus.processed
            flush_dir(frontend, scanid)
            # delete groupresult
            gr.delete()
        frontend_app.send_task("frontend.tasks.scan_result", args=(scanid, filename, probe, result))
        print "result from probe {0} for scanid {1} sent back to frontend".format(probe, scanid)
    except IrmaTaskError as e:
        return IrmaTaskReturn.error("{0}".format(e))

