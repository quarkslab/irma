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

import celery
import config.parser as config
from frontend.objects import ScanFile, ScanInfo, ScanRefResults, ScanResults
from lib.common.compat import timestamp
from lib.irma.common.exceptions import IrmaLockError
from lib.irma.common.utils import IrmaTaskReturn, IrmaScanStatus, IrmaLockMode
from lib.common.utils import humanize_time_str
from lib.irma.ftp.handler import FtpTls


frontend_app = celery.Celery('frontendtasks')
config.conf_frontend_celery(frontend_app)

scan_app = celery.Celery('scantasks')
config.conf_brain_celery(scan_app)


@frontend_app.task(acks_late=True)
def scan_launch(scanid, force):
    try:
        print("{0}: Launching with force={1}".format(scanid, force))
        scan = None
        ftp_config = config.frontend_config['ftp_brain']
        scan = ScanInfo(id=scanid, mode=IrmaLockMode.write)
        if not scan.status == IrmaScanStatus.created:
            scan.release()
            status = IrmaScanStatus.label[scan.status]
            print("{0}: Error invalid scan status:{1}".format(scanid, status))
            return IrmaTaskReturn.error("Frontend: Invalid scan status")

        # If nothing return
        if len(scan.scanfile_ids) == 0:
            scan.update_status(IrmaScanStatus.finished)
            scan.release()
            print("{0}: Error No files to scan".format(scanid))
            return IrmaTaskReturn.success("Frontend: No files to scan")

        filtered_file_oids = []
        for (scanfile_id, scanres_id) in scan.scanfile_ids.items():
            if not force:
                scan_res = ScanResults(id=scanres_id, mode=IrmaLockMode.write)
                # fetch results already present in base
                ref_res = ScanRefResults.init_id(scanfile_id)
                for (probe, results) in ref_res.results.items():
                    if probe not in scan.probelist:
                        continue
                    scan_res.results[probe] = results
                scan_res.update()
                scan_res.release()
            scan_res = ScanResults(id=scanres_id, mode=IrmaLockMode.read)
            probetodo = []
            # Compute remaining list
            for probe in scan.probelist:
                if probe not in scan_res.probedone:
                    probetodo.append(probe)
            if len(probetodo) != 0:
                scan_req = (scanfile_id, scan_res.name, probetodo)
                filtered_file_oids.append(scan_req)
        scan.update()

        # If nothing left, return
        if len(filtered_file_oids) == 0:
            scan.update_status(IrmaScanStatus.finished)
            scan.release()
            print("{0}: Success: Nothing to do".format(scanid))
            return IrmaTaskReturn.success("Frontend: Nothing to do")
        scan.release()

        host = ftp_config.host
        port = ftp_config.port
        user = ftp_config.username
        pwd = ftp_config.password
        with FtpTls(host, port, user, pwd) as ftps:
            scan_request = []
            ftps.mkdir(scanid)
            for (scanfile_id, filename, probelist) in filtered_file_oids:
                f = ScanFile(id=scanfile_id)
                # our ftp handler store file under with its sha256 name
                hashname = ftps.upload_data(scanid, f.data)
                if hashname != f.hashvalue:
                    reason = "Ftp Error: integrity failure while uploading \
                    file {0} for scanid {1}".format(scanid, filename)
                    return IrmaTaskReturn.error(reason)
                scan_request.append((hashname, probelist))
                # launch new celery task
        scan_app.send_task("brain.tasks.scan", args=(scanid, scan_request))
        scan = ScanInfo(id=scanid, mode=IrmaLockMode.write)
        scan.update_status(IrmaScanStatus.launched)
        scan.release()
        print("{0}: Success: scan launched".format(scanid))
        return IrmaTaskReturn.success("scan launched")
    except IrmaLockError as e:
        print "IrmaLockError has occurred:{0}".format(e)
        raise scan_launch.retry(countdown=15, max_retries=10)
    except Exception as e:
        if scan is not None:
            scan.release()
        print "Exception has occurred:{0}".format(e)
        raise scan_launch.retry(countdown=15, max_retries=10)


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
        scan = scan_res = ref_res = None

        scanfile = ScanFile(sha256=file_hash)
        scan = ScanInfo(id=scanid)
        if scanfile.id not in scan.scanfile_ids:
            print("{0}: fileid (%s) not found in scan info".format(scanfile.id,
                                                                   scanid))
            reason = "Frontend: filename not found in scan info"
            return IrmaTaskReturn.error(reason)

        scanfile.take()
        if scanid not in scanfile.scan_id:
            # update scanid list if not already present
            scanfile.scan_id.append(scanid)
        scanfile.date_last_scan = timestamp()
        scanfile.update()
        scanfile.release()

        sanitized_res = sanitize_dict(result)

        # Update main reference results with fresh results
        ref_res = ScanRefResults.init_id(scanfile.id, mode=IrmaLockMode.write)
        # keep uptodate results for this file in scanrefresults
        ref_res.results[probe] = sanitized_res
        ref_res.update()
        ref_res.release()

        # keep scan results into scanresults objects
        scanres_id = scan.scanfile_ids[scanfile.id]
        scan_res = ScanResults(id=scanres_id, mode=IrmaLockMode.write)
        scan_res.results[probe] = sanitized_res
        scan_res.update()
        scan_res.release()
        print("{0}: ".format(scanid) +
              "results from {0} ".format(probe) +
              "nb probedone {0} ".format(len(scan_res.probedone)))

        if scan.is_completed():
            scan.take()
            scan.update_status(IrmaScanStatus.finished)
            scan.release()

    except IrmaLockError as e:
        print ("IrmaLockError has occurred:{0}".format(e))
        raise scan_result.retry(countdown=15, max_retries=10)
    except Exception as e:
        if scan is not None:
            scan.release()
        if scan_res is not None:
            scan_res.release()
        if ref_res is not None:
            ref_res.release()
        print ("Exception has occurred:{0}".format(e))
        raise scan_result.retry(countdown=15, max_retries=10)


@frontend_app.task()
def clean_db():
    try:
        cron_cfg = config.frontend_config['cron_frontend']
        max_age_scaninfo = cron_cfg['clean_db_scan_info_max_age']
        # days to seconds
        max_age_scaninfo *= 24 * 60 * 60
        max_age_scanfile = cron_cfg['clean_db_scan_file_max_age']
        # days to seconds
        max_age_scanfile *= 24 * 60 * 60
        nb_scaninfo = ScanInfo.remove_old_instances(max_age_scaninfo)
        nb_scanfile = ScanFile.remove_old_instances(max_age_scanfile)
        hage_scaninfo = humanize_time_str(max_age_scaninfo, 'seconds')
        hage_scanfile = humanize_time_str(max_age_scanfile, 'seconds')
        print("removed {0} scan info ".format(nb_scaninfo) +
              "(older than {0})".format(hage_scaninfo))
        print("removed {0} scan files ".format(nb_scanfile) +
              "(older than {0}) ".format(hage_scanfile))
        return (nb_scaninfo, nb_scanfile)
    except Exception as e:
        print "Exception has occurred:{0}".format(e)
        raise clean_db.retry(countdown=15, max_retries=10)
