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
<<<<<<< HEAD
from frontend.nosqlobjects import ProbeRealResult
from frontend.sqlobjects import Scan, File
from lib.common import compat
=======
from frontend.nosqlobjects import ScanFile, ScanInfo, \
    ScanRefResults, ScanResults
>>>>>>> 5069fec5204c70e59aec658aa988ed98391f8f90
from lib.common.compat import timestamp
from lib.irma.common.exceptions import IrmaFileSystemError
from lib.irma.common.utils import IrmaTaskReturn, IrmaScanStatus, IrmaProbeResultsStates
from lib.common.utils import humanize_time_str
from lib.irma.database.sqlhandler import SQLDatabase
from lib.irma.ftp.handler import FtpTls


frontend_app = celery.Celery('frontendtasks')
config.conf_frontend_celery(frontend_app)

scan_app = celery.Celery('scantasks')
config.conf_brain_celery(scan_app)


@frontend_app.task(acks_late=True)
def scan_launch(scanid, force):
    try:
<<<<<<< HEAD
        session = SQLDatabase.get_session()

=======
        print("{0}: Launching with force={1}".format(scanid, force))
        scan = None
>>>>>>> 5069fec5204c70e59aec658aa988ed98391f8f90
        ftp_config = config.frontend_config['ftp_brain']
        scan = Scan.load_from_ext_id(scanid, session=session)
        if not scan.status == IrmaScanStatus.created:
<<<<<<< HEAD
            return IrmaTaskReturn.error("Invalid scan status")

        # If nothing return
        if len(scan.files_web) == 0:
            scan.status = IrmaScanStatus.finished
            scan.update(['status'], session=session)
            session.commit()
            return IrmaTaskReturn.success("No files to scan")
=======
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
>>>>>>> 5069fec5204c70e59aec658aa988ed98391f8f90

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
<<<<<<< HEAD
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
=======
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
>>>>>>> 5069fec5204c70e59aec658aa988ed98391f8f90

        host = ftp_config.host
        port = ftp_config.port
        user = ftp_config.username
        pwd = ftp_config.password
        with FtpTls(host, port, user, pwd) as ftps:
            scan_request = []
            ftps.mkdir(scanid)
            for (fw, probes_to_do) in files_web_todo:
                #for (scanfile_id, filename, probelist) in files_web_todo:
                f = fw.file
                file_data = ''
                chunk_size = 32
                path = os.path.abspath(
                    '{0}{1}'.format(config.get_samples_storage_path(), f.path)
                )
                try:
                    h = open(path, "rb")
                    chunk = h.read(chunk_size)
                    while chunk != "":
                        file_data += chunk
                        chunk = h.read(chunk_size)
                except IOError as e:
                    raise IrmaFileSystemError(e)
                finally:
                    h.close()

                # our ftp handler store file under with its sha256 name
                hashname = ftps.upload_data(scanid, file_data)
                if hashname != f.hashvalue:
                    reason = "Ftp Error: integrity failure while uploading \
                    file {0} for scanid {1}".format(scanid, fw.name)
                    return IrmaTaskReturn.error(reason)
                scan_request.append((hashname, probes_to_do))
                # launch new celery task
        scan_app.send_task("brain.tasks.scan", args=(scanid, scan_request))
<<<<<<< HEAD

        scan.status = IrmaScanStatus.launched
        scan.update(['status'], session=session)
        session.commit()
        return IrmaTaskReturn.success("scan launched")
=======
        scan = ScanInfo(id=scanid, mode=IrmaLockMode.write)
        scan.update_status(IrmaScanStatus.launched)
        scan.release()
        print("{0}: Success: scan launched".format(scanid))
        return IrmaTaskReturn.success("scan launched")
    except IrmaLockError as e:
        print "IrmaLockError has occurred:{0}".format(e)
        raise scan_launch.retry(countdown=2, max_retries=3, exc=e)
>>>>>>> 5069fec5204c70e59aec658aa988ed98391f8f90
    except Exception as e:
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
    session = SQLDatabase.get_session()

    try:
        scan = Scan.load_from_ext_id(scanid, session=session)
        fw = None

<<<<<<< HEAD
        for file_web in scan.files_web:
            if file_hash == file_web.file.sha256:
                fw = file_web
                break
        if fw is None:
            return IrmaTaskReturn.error("filename not found in scan")
=======
        scanfile = ScanFile(sha256=file_hash)
        scan = ScanInfo(id=scanid)
        if scanfile.id not in scan.scanfile_ids:
            print("{0}: fileid (%s) not found in scan info".format(scanfile.id,
                                                                   scanid))
            reason = "Frontend: filename not found in scan info"
            return IrmaTaskReturn.error(reason)
>>>>>>> 5069fec5204c70e59aec658aa988ed98391f8f90

        scan.timestamp_last_scan = compat.timestamp()
        scan.update(['timestamp_last_scan'], session=session)

        sanitized_res = sanitize_dict(result)

        # Update main reference results with fresh results
<<<<<<< HEAD
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
        #TODO add remaining parameters
        prr = ProbeRealResult(
            probe_name=pr.probe_name,
            probe_type=None,
            status=IrmaProbeResultsStates.finished,
            duration=None,
            result=None,
            results=formatted_res
        )
        pr.no_sql_id = prr.id
        pr.update(['no_sql_id'], session=session)

        print("Scanid {0}".format(scanid) +
              "Result from {0} ".format(probe) +
              "probedone {0}".format([pr.name for pr in fw.probe_results]))
=======
        ref_res = ScanRefResults.init_id(scanfile.id, mode=IrmaLockMode.write)
        # keep uptodate results for this file in scanrefresults
        ref_res.results[probe] = sanitized_res
        ref_res.update()
        ref_res.release()

        # keep scan results into scanresults objects
        scanres_id = scan.scanfile_ids[scanfile.id]
        scan_res = ScanResults(id=scanres_id, mode=IrmaLockMode.write)
        sanitized_res['success'] = True
        scan_res.results[probe] = sanitized_res
        scan_res.update()
        scan_res.release()
        print("{0}: ".format(scanid) +
              "results from {0} ".format(probe) +
              "nb probedone {0} ".format(len(scan_res.probedone)))
>>>>>>> 5069fec5204c70e59aec658aa988ed98391f8f90

        if scan.is_over():
            scan.status = IrmaScanStatus.finished
            scan.update(['status'], session=session)

        session.commit()

<<<<<<< HEAD
    except Exception as e:
        print "Exception has occurred:{0}".format(e)
        raise scan_result.retry(countdown=15, max_retries=10)
=======
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


@frontend_app.task(acks_late=True)
def scan_result_error(scanid, file_hash, probe, exc):
    try:
        scan = scan_res = ref_res = None

        scanfile = ScanFile(sha256=file_hash)
        scan = ScanInfo(id=scanid)
        if scanfile.id not in scan.scanfile_ids:
            print("{0}: fileid (%s) not found in scan info".format(scanfile.id,
                                                                   scanid))
            reason = "Frontend: filename not found in scan info"
            return IrmaTaskReturn.error(reason)

        # keep scan results into scanresults objects
        scanres_id = scan.scanfile_ids[scanfile.id]
        scan_res = ScanResults(id=scanres_id, mode=IrmaLockMode.write)
        results = {}
        results['success'] = False
        results['reason'] = exc
        scan_res.results[probe] = results
        scan_res.update()
        scan_res.release()
        print("{0}: ".format(scanid) +
              "error from {0} ".format(probe) +
              "nb probedone {0} ".format(len(scan_res.probedone)))

        if scan.is_completed():
            scan.take()
            scan.update_status(IrmaScanStatus.finished)
            scan.release()

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
>>>>>>> 5069fec5204c70e59aec658aa988ed98391f8f90


@frontend_app.task()
def clean_db():
    try:
        cron_cfg = config.frontend_config['cron_frontend']

        max_age_file = cron_cfg['clean_db_file_max_age']
        # days to seconds
        max_age_file *= 24 * 60 * 60
        nb_files = File.remove_old_files(max_age_file)
        hage_file = humanize_time_str(max_age_file, 'seconds')

        print("removed {0} files ".format(nb_files) +
              "(older than {0})".format(hage_file))

        return nb_files, 0
    except Exception as e:
        print "Exception has occurred:{0}".format(e)
        raise clean_db.retry(countdown=2, max_retries=3, exc=e)
