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

import uuid
import time
import config.parser as config

from celery import Celery
from celery.utils.log import get_task_logger
from datetime import datetime, timedelta
from brain.objects import User, Scan
from lib.irma.common.utils import IrmaTaskReturn, IrmaScanStatus
from lib.irma.common.exceptions import IrmaTaskError, IrmaDatabaseError
from lib.irma.database.sqlhandler import SQLDatabase
from lib.irma.ftp.handler import FtpTls

# Get celery's logger
log = get_task_logger(__name__)

# Time to cache the probe list
# to avoid asking to rabbitmq
PROBELIST_CACHE_TIME = 60
cache_probelist = {'list': None, 'time': None}

scan_app = Celery('scantasks')
config.conf_brain_celery(scan_app)
config.configure_syslog(scan_app)

probe_app = Celery('probetasks')
config.conf_probe_celery(probe_app)
config.configure_syslog(probe_app)

results_app = Celery('restasks')
config.conf_results_celery(results_app)
config.configure_syslog(results_app)

frontend_app = Celery('frontendtasks')
config.conf_frontend_celery(frontend_app)
config.configure_syslog(frontend_app)


# =============
#  SQL Helpers
# =============

def get_quota(sql, user):
    if user.quota == 0:
        # quota=0 means quota disabled
        quota = None
    else:
        # Quota are set per 24 hours
        delta = timedelta(hours=24)
        what = ("user_id={0} ".format(user.id) +
                "and date >= '{0}'".format(datetime.now() - delta))
        quota = user.quota - sql.sum(Scan.nbfiles, what)
    return quota


def get_groupresult(taskid):
    if not taskid:
        raise IrmaTaskError("task_id not set")
    gr = probe_app.GroupResult.restore(taskid)
    if not gr:
        raise IrmaTaskError("not a valid taskid")
    return gr


# ================
#  Celery Helpers
# ================

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


# ===============
#  Tasks Helpers
# ===============

def get_probelist():
    now = time.time()
    result_queue = config.brain_config['broker_probe'].queue
    if cache_probelist['time'] is not None:
        cache_time = now - cache_probelist['time']
    if cache_probelist['time'] is None or cache_time > PROBELIST_CACHE_TIME:
        slist = list()
        i = probe_app.control.inspect()
        queues = i.active_queues()
        if queues:
            for infolist in queues.values():
                for info in infolist:
                    if info['name'] not in slist:
                        # exclude only predefined result queue
                        if info['name'] != result_queue:
                            slist.append(info['name'])
        cache_probelist['list'] = slist
        cache_probelist['time'] = now
    return cache_probelist['list']


def flush_dir(ftpuser, scanid):
    conf_ftp = config.brain_config['ftp_brain']
    with FtpTls(conf_ftp.host,
                conf_ftp.port,
                conf_ftp.username,
                conf_ftp.password) as ftps:
        ftps.deletepath("{0}/{1}".format(ftpuser, scanid), deleteParent=True)


# ===================
#  Tasks declaration
# ===================

@scan_app.task()
def probe_list():
    return IrmaTaskReturn.success(get_probelist())


@scan_app.task(ignore_result=True)
def scan(scanid, scan_request):
    engine = config.brain_config['sql_brain'].engine
    dbname = config.brain_config['sql_brain'].dbname
    sql = SQLDatabase(engine + dbname)
    available_probelist = get_probelist()
    jobs_list = []
    # FIXME: get rmq_vhost dynamically
    rmqvhost = config.brain_config['broker_frontend'].vhost
    try:
        user = sql.one_by(User, rmqvhost=rmqvhost)
        quota = get_quota(sql, user)
        if quota is not None:
            log.debug("Found user {0} quota remaining {1}/{2}"
                      "".format(user.name, quota, user.quota))
        else:
            log.debug("Found user {0} quota disabled".format(user.name))
    except IrmaTaskError as e:
        log.exception("{0}".format(e))
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
                break
            if quota:
                quota -= 1
            callback_signature = route(
                results_app.signature("brain.tasks.scan_result",
                                      (user.ftpuser, scanid, filename, probe)))
            jobs_list.append(
                probe_app.send_task("probe.tasks.probe_scan",
                                    args=(user.ftpuser, scanid, filename),
                                    queue=probe,
                                    link=callback_signature))

    if len(jobs_list) != 0:
        # Build a result set with all job AsyncResult
        # for progress/cancel operations
        groupid = str(uuid.uuid4())
        groupres = probe_app.GroupResult(id=groupid, results=jobs_list)
        # keep the groupresult object for task status/cancel
        groupres.save()

        scan = Scan(scanid=scanid,
                    taskid=groupid,
                    nbfiles=len(jobs_list),
                    status=IrmaScanStatus.launched,
                    user_id=user.id, date=datetime.now())
        sql.add(scan)
    log.debug("{0} files receives / {1} active probe / "
              "{2} probe used / {3} jobs launched"
              "".format(len(scan_request), len(available_probelist),
                        len(probelist), len(jobs_list)))
    return


@scan_app.task()
def scan_progress(scanid):
    try:
        engine = config.brain_config['sql_brain'].engine
        dbname = config.brain_config['sql_brain'].dbname
        sql = SQLDatabase(engine + dbname)
    except Exception as e:
        return IrmaTaskReturn.error("Brain SQL: {0}".format(e))
    # FIXME: get rmq_vhost dynamically
    rmqvhost = config.brain_config['broker_frontend'].vhost
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
            if j.ready():
                nbcompleted += 1
            if j.successful():
                nbsuccessful += 1
        return IrmaTaskReturn.success({"total": len(gr),
                                       "finished": nbcompleted,
                                       "successful": nbsuccessful})
    else:
        return IrmaTaskReturn.warning(scan.status)


@scan_app.task()
def scan_cancel(scanid):
    try:
        engine = config.brain_config['sql_brain'].engine
        dbname = config.brain_config['sql_brain'].dbname
        sql = SQLDatabase(engine + dbname)
        # FIXME: get rmq_vhost dynamically
        rmqvhost = config.brain_config['broker_frontend'].vhost
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
            flush_dir(user.ftpuser, scanid)
            return IrmaTaskReturn.success({"total": len(gr),
                                           "finished": nbcompleted,
                                           "cancelled": nbcancelled})
        else:
            return IrmaTaskReturn.warning(scan.status)
    except IrmaTaskError as e:
        return IrmaTaskReturn.error("{0}".format(e))


@results_app.task(ignore_result=True)
def scan_result(result, ftpuser, scanid, filename, probe):
    try:
        frontend_app.send_task("frontend.tasks.scan_result",
                               args=(scanid, filename, probe, result))
        log.debug("scanid {0} sent result {1}".format(scanid, probe))
        engine = config.brain_config['sql_brain'].engine
        dbname = config.brain_config['sql_brain'].dbname
        sql = SQLDatabase(engine + dbname)
        # FIXME get rmq_vhost dynamically
        rmqvhost = config.brain_config['broker_frontend'].vhost
        user = sql.one_by(User, rmqvhost=rmqvhost)
        scan = sql.one_by(Scan, scanid=scanid, user_id=user.id)
        gr = get_groupresult(scan.taskid)
        nbtotal = len(gr)
        nbcompleted = nbsuccessful = 0
        for j in gr:
            if j.ready():
                nbcompleted += 1
            if j.successful():
                nbsuccessful += 1
        if nbtotal == nbcompleted:
            scan.status = IrmaScanStatus.processed
            flush_dir(ftpuser, scanid)
            # delete groupresult
            gr.delete()
    except IrmaTaskError as e:
        return IrmaTaskReturn.error("{0}".format(e))
