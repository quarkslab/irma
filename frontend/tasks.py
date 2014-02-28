import celery
import config
from frontend.objects import ScanFile, ScanInfo, ScanResults
from lib.irma.common.exceptions import IrmaFtpError, IrmaTaskError, \
    IrmaDatabaseError
from lib.irma.common.utils import IrmaTaskReturn
from lib.irma.ftp.handler import FtpTls

frontend_app = celery.Celery('frontendtasks')
config.conf_frontend_celery(frontend_app)

scan_app = celery.Celery('scantasks')
config.conf_brain_celery(scan_app)

@frontend_app.task
def scan_launch(scanid, force):
    ftp_config = config.frontend_config['ftp_brain']
    try:
        scan = ScanInfo(id=scanid)
        if not scan.is_launchable():
            return IrmaTaskReturn.error("Invalid scan status")

        # If nothing return
        if len(scan.oids) == 0:
            scan.finished()
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
            scan.finished()
            return IrmaTaskReturn.success("Nothing to do")

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
        scan.launched()
    except IrmaFtpError as e:
        return IrmaTaskReturn.error("Ftp Error: {0}".format(e))
    return IrmaTaskReturn.success("scan launched")

@frontend_app.task(ignore_result=True)
def scan_result(scanid, file_hash, probe, result):
    try:
        scan = ScanInfo(id=scanid)
        for (file_oid, file_info) in scan.oids.items():
            f = ScanFile(id=file_oid)
            if f.hashvalue == file_hash:
                break
        if f.hashvalue != file_hash:
            return IrmaTaskReturn.error("filename not found in scan info")
        filename = file_info['name']

        assert file_oid == f.id
        scan_res = ScanResults.init_id(file_oid)
        assert scan_res.id == file_oid
        if probe not in scan_res.probelist:
            scan_res.probelist.append(probe)
        assert probe not in file_info['probedone']
        file_info['probedone'].append(probe)
        print "Update result of file {0} with {1}:{2}".format(filename, probe, result)
        scan_res.results[probe] = result
        scan_res.save()
        scan.check_completed()
    except IrmaDatabaseError as e:
        return IrmaTaskReturn.error(str(e))
