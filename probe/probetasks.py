import importlib, tempfile, celery
import config
from lib.irma.common.utils import IrmaTaskReturn
from lib.irma.fileobject.handler import FileObject
from lib.irma.ftp.handler import FtpTls

probe_celery = celery.Celery()
config.conf_probe_celery(probe_celery)

brain_celery = celery.Celery()
config.conf_brain_celery(brain_celery)

@brain_celery.task()
def scan_error():
    pass

@brain_celery.task()
def scan_result():
    pass

mscan = importlib.import_module("probe." + config.probe_config.probe.avname)

@probe_celery.task()
def probe_scan(frontend, scanid, filename):
    conf_ftp = config.probe_config.ftp_brain
    with FtpTls(conf_ftp.host, conf_ftp.port, conf_ftp.username, conf_ftp.password) as ftps:
        _, tmpname = tempfile.mkstemp()
        ftps.download("{0}/{1}".format(frontend, scanid), filename, tmpname)
        results = mscan.scan(tmpname)
    return results

