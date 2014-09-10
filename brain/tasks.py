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
        msg = "SQL: task_id not set"
        log.debug(msg)
        raise IrmaTaskError()
    gr = probe_app.GroupResult.restore(taskid)
    if not gr:
        msg = "SQL: taskid not valid"
        log.debug(msg + " [{0}]".format(taskid))
        raise IrmaTaskError(msg)
    return gr


def sql_connect(engine, dbname):
    try:
        return SQLDatabase(engine + dbname)
    except Exception as e:
        msg = "SQL: can't connect"
        log.debug(msg + " [{0}]".format(e))
        raise IrmaTaskError(msg)


def sql_get_user(sql, rmqvhost=None):
    # FIXME: get rmq_vhost dynamically
    try:
        if rmqvhost is None:
            rmqvhost = config.brain_config['broker_frontend'].vhost
        return sql.one_by(User, rmqvhost=rmqvhost)
    except Exception as e:
        msg = "SQL: user not found"
        log.debug(msg + " [{0}]".format(e))
        raise IrmaTaskError(msg)


def sql_get_scan(sql, scanid, user):
    try:
        return sql.one_by(Scan, scanid=scanid, user_id=user.id)
    except Exception as e:
        msg = "SQL: scan id not found"
        log.debug(msg + " [{0}]".format(e))
        raise IrmaTaskError(msg)


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
        if len(slist) != 0:
            # activate cache only on non empty list
            cache_probelist['time'] = now
        cache_probelist['list'] = slist
    return cache_probelist['list']


def flush_dir(ftpuser, scanid):
    print("Flushing dir {0}".format(scanid))
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
    probe_list = get_probelist()
    if len(probe_list) > 0:
        return IrmaTaskReturn.success(get_probelist())
    else:
        return IrmaTaskReturn.error("No probe available")


@scan_app.task(ignore_result=True)
def scan(scanid, scan_request):
    engine = config.brain_config['sql_brain'].engine
    dbname = config.brain_config['sql_brain'].dbname
    sql = sql_connect(engine, dbname)
    available_probelist = get_probelist()
    jobs_list = []
    # create an initial entry to track future errors
    scan = Scan(scanid=scanid,
                status=IrmaScanStatus.empty,
                date=datetime.now())
    sql.add(scan)
    sql.commit()
    try:
        # tell frontend that scanid is now known to brain
        # progress available
        frontend_app.send_task("frontend.tasks.scan_launched",
                               args=[scanid])
        user = sql_get_user(sql)
        quota = get_quota(sql, user)
        if quota is not None:
            log.debug("{0} : Found user {1} ".format(scanid, user.name) +
                      "quota remaining {0}/{1}".format(quota, user.quota))
        else:
            log.debug("{0} : Found user {1} quota disabled"
                      "".format(scanid, user.name))
        scan.user_id = user.id
        sql.commit()

        for (filename, probelist) in scan_request.items():
            if probelist is None:
                scan.status = IrmaScanStatus.error_probe_missing
                sql.commit()
                log.debug("{0}: Empty probe list".format(scanid))
                return IrmaTaskReturn.error("BrainTask: Empty probe list")
            # first check probelist
            for p in probelist:
                # check if probe exists
                if p not in available_probelist:
                    scan.status = IrmaScanStatus.error_probe_na
                    sql.commit()
                    msg = "BrainTask: Unknown probe {0}".format(p)
                    log.debug("{0}: Unknown probe {1}".format(scanid, p))
                    return IrmaTaskReturn.error(msg)

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

            scan.taskid = groupid
            scan.nbfiles = len(jobs_list)
            scan.status = IrmaScanStatus.launched
            sql.commit()

        log.debug(
            "{0}: ".format(scanid) +
            "{0} files receives / ".format(len(scan_request)) +
            "{0} active probe / ".format(len(available_probelist)) +
            "{0} probe used / ".format(len(probelist)) +
            "{0} jobs launched".format(len(jobs_list)))

    except Exception as e:
        scan_flush(scanid)
        scan.status = IrmaScanStatus.error
        sql.commit()
        log.debug("{0} : Error {1}".format(scanid, e))
        return


@scan_app.task()
def scan_progress(scanid):
    log.debug("{0}: scan progress".format(scanid))
    engine = config.brain_config['sql_brain'].engine
    dbname = config.brain_config['sql_brain'].dbname
    try:
        sql = sql_connect(engine, dbname)
        user = sql_get_user(sql)
        scan = sql_get_scan(sql, scanid, user)
        res = {}
        if IrmaScanStatus.is_error(scan.status):
            status_str = IrmaScanStatus.label[scan.status]
            msg = "Brain: scan error ({0})".format(status_str)
            return IrmaTaskReturn.error(msg)
        res['status'] = IrmaScanStatus.label[scan.status]
        res['progress_details'] = None
        if scan.status == IrmaScanStatus.launched:
            if not scan.taskid:
                log.debug("{0}: sql no task_id".format(scanid))
                msg = "Brain: task id not set (SQL)"
                return IrmaTaskReturn.error(msg)
            gr = get_groupresult(scan.taskid)
            nbcompleted = nbsuccessful = 0
            for j in gr:
                if j.ready():
                    nbcompleted += 1
                if j.successful():
                    nbsuccessful += 1
            res['progress_details'] = {}
            res['progress_details']['total'] = len(gr)
            res['progress_details']['finished'] = nbcompleted
            res['progress_details']['successful'] = nbsuccessful
        return IrmaTaskReturn.success(res)
    except IrmaTaskError as e:
        msg = "Brain: progress error {0}".format(e)
        return IrmaTaskReturn.error(msg)


@scan_app.task()
def scan_cancel(scanid):
    try:
        engine = config.brain_config['sql_brain'].engine
        dbname = config.brain_config['sql_brain'].dbname
        sql = sql_connect(engine, dbname)
        user = sql_get_user(sql)
        scan = sql_get_scan(sql, scanid, user)
        res = {}
        res['status'] = IrmaScanStatus.label[scan.status]
        res['cancel_details'] = None
        if IrmaScanStatus.is_error(scan.status):
            scan_flush(scanid)
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
            sql.commit()
            scan_flush(scanid)
            res['cancel_details'] = {}
            res['cancel_details']['total'] = len(gr)
            res['cancel_details']['finished'] = nbcompleted
            res['cancel_details']['cancelled'] = nbcancelled
        return IrmaTaskReturn.success(res)
    except IrmaTaskError as e:
        msg = "Brain: cancel error {0}".format(e)
        return IrmaTaskReturn.error(msg)


@results_app.task(ignore_result=True)
def scan_result(result, ftpuser, scanid, filename, probe):
    try:
        frontend_app.send_task("frontend.tasks.scan_result",
                               args=(scanid, filename, probe, result))
        log.debug("{0} sent result {1}".format(scanid, probe))
        engine = config.brain_config['sql_brain'].engine
        dbname = config.brain_config['sql_brain'].dbname
        sql = sql_connect(engine, dbname)
        user = sql_get_user(sql)
        scan = sql_get_scan(sql, scanid, user)
        gr = get_groupresult(scan.taskid)
        nbtotal = len(gr)
        nbcompleted = nbsuccessful = 0
        for j in gr:
            if j.ready():
                nbcompleted += 1
            if j.successful():
                nbsuccessful += 1
        if nbtotal == nbcompleted:
            # update scan status
            scan.status = IrmaScanStatus.processed
            sql.commit()
    except IrmaTaskError as e:
        msg = "Brain: result error {0}".format(e)
        return IrmaTaskReturn.error(msg)


@results_app.task(ignore_result=True)
def scan_flush(scanid):
    try:
        log.debug("{0} scan flush requested".format(scanid))
        engine = config.brain_config['sql_brain'].engine
        dbname = config.brain_config['sql_brain'].dbname
        sql = sql_connect(engine, dbname)
        user = sql_get_user(sql)
        scan = sql_get_scan(sql, scanid, user)
        if not IrmaScanStatus.is_error(scan.status):
            log.debug("{0} deleting group results entry".format(scanid))
            gr = get_groupresult(scan.taskid)
            # delete groupresult
            gr.delete()
            # remove directory
        log.debug("{0} deleting files".format(scanid))
        flush_dir(user.ftpuser, scanid)
    except Exception as e:
        log.debug("{0} flush error {1}".format(scanid, e))
        return
