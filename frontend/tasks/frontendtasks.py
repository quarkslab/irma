import celery
import config
from frontend.objects import ScanFile
from lib.irma.common.exceptions import IrmaFtpError
from lib.irma.common.utils import IrmaTaskReturn
from lib.irma.ftp.handler import FtpTls


frontend_app = celery.Celery('frontendtasks')
config.conf_frontend_celery(frontend_app)

scan_app = celery.Celery('scantasks')
config.conf_brain_celery(scan_app)

@frontend_app.task
def scan_launch(scanid, file_oids, probelist, force):
    ftp_config = config.frontend_config['ftp_brain']
    try:
        filtered_file_oids = [(oid, filename, probelist) for (oid, filename) in file_oids.items()]
        if not force:
            # remove files already scanned
            # FIXME check probelist results available
            pass

        # If nothing left return
        if len(filtered_file_oids) == 0:
            return IrmaTaskReturn.success("No files to scan")

        with FtpTls(ftp_config.host, ftp_config.port, ftp_config.username, ftp_config.password) as ftps:
            scan_request = []
            ftps.mkdir(scanid)
            for (oid, filename, probelist) in filtered_file_oids:
                f = ScanFile(_id=oid)
                # our ftp handler store file under with its sha256 name
                hashname = ftps.upload_data(scanid, f.data)
                if hashname != f.hashvalue:
                    return IrmaTaskReturn.error("Ftp Error: integrity failure while uploading file {0} for scanid {1}".format(scanid, filename))
                scan_request.append((hashname, probelist))
                # launch new celery task
        scan_app.send_task("brain.tasks.scantasks.scan", args=(scanid, scan_request))
    except IrmaFtpError as e:
        return IrmaTaskReturn.error("Ftp Error: {0}".format(e))
    return IrmaTaskReturn.success("scan launched")
