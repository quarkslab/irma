import celery
import config
import ftplib
from frontend.lib.objects import ScanFile
from lib.irma.common.exceptions import IrmaFtpError
from lib.irma.common.utils import IrmaTaskReturn
from lib.irma.ftp.handler import FtpTls


frontend_celery = celery.Celery()
config.conf_frontend_celery(frontend_celery)

brain_celery = celery.Celery()
config.conf_brain_celery(brain_celery)

@frontend_celery.task
def scan_launch(scanid, file_oids, probelist, force):
    ftp_config = config.frontend_config.ftp_brain
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
                brain_celery.send_task("brain.braintasks.scan", args=(scanid, scan_request))
    except IrmaFtpError as e:
        return IrmaTaskReturn.error("Ftp Error: {0}".format(e))
    return IrmaTaskReturn.success("scan launched")
