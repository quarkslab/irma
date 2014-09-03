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

import os
import celery
import config.parser as config

from celery.utils.log import get_task_logger
from frontend.models.nosqlobjects import ProbeRealResult
from frontend.models.sqlobjects import Scan, File, sql_db_connect
from lib.common import compat
from lib.irma.common.utils import IrmaTaskReturn, IrmaScanStatus, \
    IrmaProbeResultsStates
from lib.irma.database.sqlhandler import SQLDatabase
from lib.common.utils import humanize_time_str
import frontend.controllers.scanctrl as scan_ctrl


log = get_task_logger(__name__)

# declare a new application
frontend_app = celery.Celery('frontendtasks')
config.conf_frontend_celery(frontend_app)
config.configure_syslog(frontend_app)

# declare a new application
scan_app = celery.Celery('scantasks')
config.conf_brain_celery(scan_app)
config.configure_syslog(scan_app)


@frontend_app.task(acks_late=True)
def scan_launch(scanid, force):
    try:
        scan_ctrl.launch_asynchronous(scanid, force)
    except Exception as e:
        print "Exception has occurred:{0}".format(e)
        raise scan_launch.retry(countdown=2, max_retries=3, exc=e)


@frontend_app.task(acks_late=True)
def scan_launched(scanid):
    try:
        print("Scanid {0} launched".format(scanid))
        session = None
        sql_db_connect()
        session = SQLDatabase.get_session()
        scan = Scan.load_from_ext_id(scanid, session=session)
        if scan.status == IrmaScanStatus.uploaded:
            scan.status = IrmaScanStatus.launched
            scan.update(['status'], session=session)
            session.commit()
    except Exception as e:
        if session is not None:
            session.rollback()
        print "Exception has occurred:{0}".format(e)
        raise scan_launch.retry(countdown=2, max_retries=3, exc=e)


def sanitize_dict(d):
    new = {}
    for k, v in d.iteritems():
        if isinstance(v, dict):
            v = sanitize_dict(v)
        newk = k.replace('.', '_').replace('$', '')
        new[newk] = v
    return new


@frontend_app.task(acks_late=True)
def scan_result(scanid, file_hash, probe, result):
    try:
        sql_db_connect()
        session = SQLDatabase.get_session()
        scan = Scan.load_from_ext_id(scanid, session=session)
        fws = []

        for file_web in scan.files_web:
            if file_hash == file_web.file.sha256:
                fws.append(file_web)
        if len(fws) == 0:
            return IrmaTaskReturn.error("filename not found in scan")

        fws[0].file.timestamp_last_scan = compat.timestamp()
        fws[0].file.update(['timestamp_last_scan'], session=session)

        sanitized_res = sanitize_dict(result)

        # update results for all files with same sha256
        for fw in fws:
            # Update main reference results with fresh results
            pr = None
            ref_res_names = [rr.probe_name for rr in fw.file.ref_results]
            for probe_result in fw.probe_results:
                if probe_result.probe_name == probe:
                    pr = probe_result
                    if probe_result.probe_name not in ref_res_names:
                        fw.file.ref_results.append(probe_result)
                    else:
                        for rr in fw.file.ref_results:
                            if probe_result.probe_name == rr.probe_name:
                                fw.file.ref_results.remove(rr)
                                fw.file.ref_results.append(probe_result)
                                break
                    break
            fw.file.update(session=session)

            # save the results
            # TODO add remaining parameters
            s_duration = sanitized_res.get('duration', None)
            s_type = sanitized_res.get('type', None)
            s_name = sanitized_res.get('name', None)
            s_version = sanitized_res.get('version', None)
            s_results = sanitized_res.get('results', None)
            s_retcode = sanitized_res.get('status', None)

            prr = ProbeRealResult(
                probe_name=s_name,
                probe_type=s_type,
                probe_version=s_version,
                status=IrmaProbeResultsStates.finished,
                duration=s_duration,
                retcode=s_retcode,
                results=s_results
            )
            pr.nosql_id = prr.id
            pr.state = IrmaProbeResultsStates.finished
            pr.update(['nosql_id', 'state'], session=session)
            probedone = [pr.probe_name for pr in fw.probe_results if pr.state == IrmaProbeResultsStates.finished]
            print("Scanid {0}".format(scanid) +
                  "Result from {0} ".format(probe) +
                  "probedone {0}".format(probedone))

        if scan.finished():
            scan.status = IrmaScanStatus.finished
            scan.update(['status'], session=session)
            # launch flush celery task on brain
            scan_app.send_task("brain.tasks.scan_flush", args=[scanid])

        session.commit()

    except Exception as e:
        print "Exception has occurred:{0}".format(e)
        raise scan_result.retry(countdown=2, max_retries=3)


@frontend_app.task()
def clean_db():
    try:
        sql_db_connect()
        session = SQLDatabase.get_session()

        cron_cfg = config.frontend_config['cron_frontend']

        max_age_file = cron_cfg['clean_db_file_max_age']
        # days to seconds
        max_age_file *= 24 * 60 * 60
        nb_files = File.remove_old_files(max_age_file, session=session)
        hage_file = humanize_time_str(max_age_file, 'seconds')

        print("removed {0} files ".format(nb_files) +
              "(older than {0})".format(hage_file))

        return nb_files, 0
    except Exception as e:
        print "Exception has occurred:{0}".format(e)
        raise clean_db.retry(countdown=2, max_retries=3, exc=e)
