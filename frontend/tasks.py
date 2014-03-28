import celery
import config.parser as config
from frontend.objects import ScanFile, ScanInfo, ScanRefResults, ScanResults
from lib.common.compat import timestamp
from lib.irma.common.exceptions import IrmaLockError
from lib.irma.common.utils import IrmaTaskReturn, IrmaScanStatus, IrmaLockMode
from lib.common.utils import  humanize_time_str
from lib.irma.ftp.handler import FtpTls
from format import format_result


frontend_app = celery.Celery('frontendtasks')
config.conf_frontend_celery(frontend_app)

scan_app = celery.Celery('scantasks')
config.conf_brain_celery(scan_app)


@frontend_app.task(acks_late=True)
def scan_launch(scanid, force):
    try:
        scan = None
        ftp_config = config.frontend_config['ftp_brain']
        scan = ScanInfo(id=scanid, mode=IrmaLockMode.write)
        if not scan.status == IrmaScanStatus.created:
            scan.release()
            return IrmaTaskReturn.error("Invalid scan status")

        # If nothing return
        if len(scan.scanfile_ids) == 0:
            scan.update_status(IrmaScanStatus.finished)
            scan.release()
            return IrmaTaskReturn.success("No files to scan")

        filtered_file_oids = []
        for (scanfile_id, scanres_id) in scan.scanfile_ids.items():
            scan_res = ScanResults(id=scanres_id, mode=IrmaLockMode.write)
            if not force:
                # fetch results already present in base
                for (probe, results) in ScanRefResults.init_id(scanfile_id).results.items():
                    if scan.probelist is not None and probe not in scan.probelist:
                        continue
                    scan_res.results[probe] = results
            scan_res.update()
            scan_res.release()
            # Compute remaining list
            probetodo = [probe for probe in scan.probelist if probe not in scan_res.probedone]
            if len(probetodo) != 0:
                filtered_file_oids.append((scanfile_id, scan_res.name, probetodo))
        scan.update()

        # If nothing left, return
        if len(filtered_file_oids) == 0:
            scan.update_status(IrmaScanStatus.finished)
            scan.release()
            return IrmaTaskReturn.success("Nothing to do")
        scan.release()

        with FtpTls(ftp_config.host, ftp_config.port, ftp_config.username, ftp_config.password) as ftps:
            scan_request = []
            ftps.mkdir(scanid)
            for (scanfile_id, filename, probelist) in filtered_file_oids:
                f = ScanFile(id=scanfile_id)
                # our ftp handler store file under with its sha256 name
                hashname = ftps.upload_data(scanid, f.data)
                if hashname != f.hashvalue:
                    return IrmaTaskReturn.error("Ftp Error: integrity failure while uploading file {0} for scanid {1}".format(scanid, filename))
                scan_request.append((hashname, probelist))
                # launch new celery task
        scan_app.send_task("brain.tasks.scan", args=(scanid, scan_request))
        scan = ScanInfo(id=scanid, mode=IrmaLockMode.write)
        scan.update_status(IrmaScanStatus.launched)
        scan.release()
        return IrmaTaskReturn.success("scan launched")
    except IrmaLockError as e:
        print "IrmaLockError has occurred:{0}".format(e)
        raise scan_launch.retry(countdown=15, max_retries=10)
    except Exception as e:
        if scan is not None: scan.release()
        print "Exception has occurred:{0}".format(e)
        raise scan_launch.retry(countdown=15, max_retries=10)


@frontend_app.task(acks_late=True)
def scan_result(scanid, file_hash, probe, result):
    try:
        scan = scan_res = None
        scan = ScanInfo(id=scanid, mode=IrmaLockMode.read)
        for (file_oid, scanres_id) in scan.scanfile_ids.items():
            scanfile = ScanFile(id=file_oid)
            if scanfile.hashvalue == file_hash:
                break
        if scanfile.hashvalue != file_hash:
            return IrmaTaskReturn.error("filename not found in scan info")
        assert file_oid == scanfile.id

        scanfile.take()
        if scanid not in scanfile.scan_id:
            # update scanid list if not alreadypresent
            scanfile.scan_id.append(scanid)
        scanfile.date_last_scan = timestamp()
        scanfile.update()
        scanfile.release()

        try:
            formatted_res = format_result(probe, result)
        except:
            formatted_res = {'result':"parsing error", 'version':None}

        # keep scan results into scanresults objects
        scan_res = ScanResults(id=scanres_id, mode=IrmaLockMode.write)
        scan_res.results[probe] = formatted_res
        scan_res.update()
        scan_res.release()
        print "Scanid [{0}] Result from {1} probedone {2}".format(scanid, probe, scan_res.probedone)

        # Update main reference results with fresh results
        ref_res = ScanRefResults.init_id(file_oid, mode=IrmaLockMode.write)
        # keep uptodate results for this file in scanrefresults
        ref_res.results[probe] = formatted_res
        ref_res.update()
        ref_res.release()

        scan = ScanInfo(id=scanid, mode=IrmaLockMode.write)
        if scan.is_completed():
            scan.update_status(IrmaScanStatus.finished)
        scan.release()

    except IrmaLockError as e:
        print "IrmaLockError has occurred:{0}".format(e)
        raise scan_result.retry(countdown=15, max_retries=10)
    except Exception as e:
        if scan is not None: scan.release()
        if scan_res is not None: scan_res.release()
        if ref_res is not None: ref_res.release()
        print "Exception has occurred:{0}".format(e)
        raise scan_result.retry(countdown=15, max_retries=10)


@frontend_app.task()
def clean_db():
    try:
        max_age_scaninfo = config.frontend_config['cron_frontend']['clean_db_scan_info_max_age']
        max_age_scanfile = config.frontend_config['cron_frontend']['clean_db_scan_file_max_age']
        nb_scaninfo = ScanInfo.remove_old_instances(max_age_scaninfo * 24 * 60 * 60)
        nb_scanfile = ScanFile.remove_old_instances(max_age_scanfile * 24 * 60 * 60)
        print "removed {0} scan info (older than {1})".format(nb_scaninfo, humanize_time_str(max_age_scaninfo, 'days'))
        print "removed {0} scan files (older than {1}) ".format(nb_scanfile, humanize_time_str(max_age_scanfile, 'days'))
        return (nb_scaninfo, nb_scanfile)
    except Exception as e:
        print "Exception has occurred:{0}".format(e)
        raise clean_db.retry(countdown=15, max_retries=10)

