import celery
import config.parser as config
from frontend.objects import ScanFile, ScanInfo, ScanResults
from lib.common.compat import timestamp
from lib.irma.common.exceptions import IrmaLockError
from lib.irma.common.utils import IrmaTaskReturn, IrmaScanStatus, IrmaLockMode
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
            return IrmaTaskReturn.error("Invalid scan status")

        # If nothing return
        if len(scan.oids) == 0:
            scan.update_status(IrmaScanStatus.finished)
            scan.release()
            return IrmaTaskReturn.success("No files to scan")

        filtered_file_oids = []
        for (oid, info) in scan.oids.items():
            if force:
                # remove results already present
                info['probedone'] = []
            elif scan.probelist is not None:
                # filter probe_done with asked probelist
                info['probedone'] = [probe for probe in info['probedone'] if probe in scan.probelist]
            # Compute remaining list
            probetodo = [probe for probe in scan.probelist if probe not in info['probedone']]
            if len(probetodo) != 0:
                filtered_file_oids.append((oid, info['name'], probetodo))

        # If nothing left, return
        if len(filtered_file_oids) == 0:
            scan.update_status(IrmaScanStatus.finished)
            scan.release()
            return IrmaTaskReturn.success("Nothing to do")
        scan.update()
        scan.release()

        with FtpTls(ftp_config.host, ftp_config.port, ftp_config.username, ftp_config.password) as ftps:
            scan_request = []
            ftps.mkdir(scanid)
            for (oid, filename, probelist) in filtered_file_oids:
                f = ScanFile(id=oid)
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
        for file_oid in scan.oids.keys():
            f = ScanFile(id=file_oid)
            if f.hashvalue == file_hash:
                break
        if f.hashvalue != file_hash:
            return IrmaTaskReturn.error("filename not found in scan info")
        assert file_oid == f.id

        scan_res = ScanResults.init_id(file_oid, mode=IrmaLockMode.write)
        scan = ScanInfo(id=scanid, mode=IrmaLockMode.write)
        if probe not in scan_res.probelist:
            scan_res.probelist.append(probe)
        if probe not in scan.oids[file_oid]['probedone']:
            scan.oids[file_oid]['probedone'].append(probe)
        else:
            print "Warning: Scanid {0} Probe {1} already tagged as 'done'".format(scanid, probe)
        print "Scanid [{0}] Result from {1} probedone {2}".format(scanid, probe, scan.oids[file_oid]['probedone'])
        try:
            scan_res.results[probe] = format_result(probe, result)
        except:
            scan_res.results[probe] = {'result':"parsing error", 'version':None}
        scan_res.update()
        scan_res.release()
        scan.update()
        if scan.is_completed():
            scan.update_status(IrmaScanStatus.finished)
        scan.release()
    except IrmaLockError as e:
        print "IrmaLockError has occurred:{0}".format(e)
        raise scan_result.retry(countdown=15, max_retries=10)
    except Exception as e:
        if scan is not None: scan.release()
        if scan_res is not None: scan_res.release()
        print "Exception has occurred:{0}".format(e)
        raise scan_result.retry(countdown=15, max_retries=10)


@frontend_app.task()
def clean_db():
    try:
        result = ScanInfo.find(
            {'date': {'$lt': timestamp() - config.frontend_config['cron_frontend']['clean_db']['scan_info_max_age']}},
            ['_id']
        )
        for sI in result:
            temp_scan_info = ScanInfo.get_temp_instance(sI['_id'])
            temp_scan_info.remove()
    except Exception as e:
        print "Exception has occurred:{0}".format(e)
        raise clean_db.retry(countdown=15, max_retries=10)

