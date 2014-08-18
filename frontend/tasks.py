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
from frontend.nosqlobjects import ProbeRealResult
from frontend.sqlobjects import Scan, File, sql_db_connect
from lib.common import compat
from lib.irma.common.exceptions import IrmaFileSystemError
from lib.irma.common.utils import IrmaTaskReturn, IrmaScanStatus, IrmaProbeResultsStates
from lib.common.utils import humanize_time_str
from lib.irma.ftp.handler import FtpTls


frontend_app = celery.Celery('frontendtasks')
config.conf_frontend_celery(frontend_app)

scan_app = celery.Celery('scantasks')
config.conf_brain_celery(scan_app)


@frontend_app.task(acks_late=True)
def scan_launch(scanid, force):
    try:
        sql_db_connect()
        session = SQLDatabase.get_session()
        ftp_config = config.frontend_config['ftp_brain']
        scan = Scan.load_from_ext_id(scanid, session=session)
        if not scan.status == IrmaScanStatus.created:
            return IrmaTaskReturn.error("Invalid scan status")

        # If nothing return
        if len(scan.files_web) == 0:
            scan.status = IrmaScanStatus.finished
            scan.update(['status'], session=session)
            session.commit()
            return IrmaTaskReturn.success("No files to scan")

        files_web_todo = []
        for fw in scan.files_web:
            probes_to_do = []
            for name in fw.probe_results.probe_name:
                probes_to_do.append(name)

            if not force:
                # Fetch the ref results for the file
                for rr in fw.file.ref_results:
                    if rr.probe_name not in probes_to_do:
                        continue
                    # Scan already done
                    probes_to_do.remove(rr.probe_name)
                    fw.probe_results.append(rr)
                fw.update(session=session)

            if len(probes_to_do) > 0:
                files_web_todo.append(
                    (fw, probes_to_do)
                )

        # Nothing to do
        if len(files_web_todo) == 0:
            scan.status = IrmaScanStatus.finished
            scan.update(['status'], session=session)
            session.commit()
            return IrmaTaskReturn.success("Nothing to do")

        host = ftp_config.host
        port = ftp_config.port
        user = ftp_config.username
        pwd = ftp_config.password
        with FtpTls(host, port, user, pwd) as ftps:
            scan_request = []
            ftps.mkdir(scanid)
            # our ftp handler store file under with its sha256 name
            common_path = config.get_samples_storage_path()
            file_sha256 = fw.file.sha256
            file_path = os.path.join(common_path, file_sha256)
            hashname = ftps.upload_file(scanid, file_path)
            if hashname != file_sha256:
                reason = "Ftp Error: integrity failure while uploading \
                file {0} for scanid {1}".format(scanid, fw.name)
                return IrmaTaskReturn.error(reason)
            scan_request.append((hashname, probes_to_do))
        # launch new celery task
        scan_app.send_task("brain.tasks.scan", args=(scanid, scan_request))

        scan.status = IrmaScanStatus.launched
        scan.update(['status'], session=session)
        session.commit()
        return IrmaTaskReturn.success("scan launched")
    except IrmaLockError as e:
        print "IrmaLockError has occurred:{0}".format(e)
        raise scan_launch.retry(countdown=2, max_retries=3, exc=e)
    except Exception as e:
        if scan is not None:
            scan.release()
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
        fw = None

        for file_web in scan.files_web:
            if file_hash == file_web.file.sha256:
                fw = file_web
                break
        if fw is None:
            return IrmaTaskReturn.error("filename not found in scan")

        scan.timestamp_last_scan = compat.timestamp()
        scan.update(['timestamp_last_scan'], session=session)

        sanitized_res = sanitize_dict(result)

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
        prr = ProbeRealResult(
            probe_name=pr.probe_name,
            probe_type=None,
            status=IrmaProbeResultsStates.finished,
            duration=None,
            result=None,
            results=sanitized_res
        )
        pr.no_sql_id = prr.id
        pr.update(['no_sql_id'], session=session)

        print("Scanid {0}".format(scanid) +
              "Result from {0} ".format(probe) +
              "probedone {0}".format([pr.name for pr in fw.probe_results]))

        if scan.is_over():
            scan.status = IrmaScanStatus.finished
            scan.update(['status'], session=session)

        session.commit()

    except Exception as e:
        print "Exception has occurred:{0}".format(e)
        raise scan_result.retry(countdown=15, max_retries=10)


@frontend_app.task(acks_late=True)
def scan_result_error(scanid, file_hash, probe, exc):
    try:
        sql_db_connect()
        session = SQLDatabase.get_session()

        file = File.load_from_sha256(file_hash, session=session)
        scan = Scan.load_from_ext_id(scanid, session=session)

        fw = None
        ok = False
        for file_web in scan.files_web:
            if file_web.file == file:
                fw = file_web
                ok = True

        if not ok:
            print("{0}: file (%s) not found in scan".format(file.sha256,
                                                            scanid))
            reason = "Frontend: filename not found in scan info"
            return IrmaTaskReturn.error(reason)

        ok = False
        pr = None
        for probe_res in fw.probe_results:
            if probe_res.name == probe:
                pr = probe_res
        if not ok:
            print(
                "{0}: probe result (%s) not found for file web".format(
                    probe,
                    file.sha256
                )
            )
            reason = "Frontend: probe result not found for file"
            return IrmaTaskReturn.error(reason)

        pRR = ProbeRealResult(
            probe_name=probe,
            probe_type=None,
            result=IrmaProbeResultsStates.error,
            results={
                'success': False,
                'reason': exc
            }
        )
        pr.no_sql_id = pRR.id
        pr.update(['no_sql_id'], session=session)

        print("{0}: ".format(scanid) +
              "error from {0} ".format(probe) +
              "nb probedone {0} ".format(len(
                  [probe_res for probe_res in fw.probe_results])))

        if scan.is_completed():
            scan.status = IrmaScanStatus.finished
            scan.update(['status'], session=session)
        session.commit()

    except IrmaLockError as e:
        print ("IrmaLockError has occurred:{0}".format(e))
        raise scan_result.retry(countdown=2, max_retries=3, exc=e)
    except Exception as e:
        if scan is not None:
            scan.release()
        if scan_res is not None:
            scan_res.release()
        if ref_res is not None:
            ref_res.release()
        print ("Exception has occurred:{0}".format(e))
        raise scan_result.retry(countdown=2, max_retries=3, exc=e)


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
