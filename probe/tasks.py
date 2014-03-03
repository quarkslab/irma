import importlib, tempfile, celery
import config
import os
from lib.irma.ftp.handler import FtpTls

probe_app = celery.Celery('probetasks')
config.conf_probe_celery(probe_app)

mscan = importlib.import_module("probe." + config.probe_config['probe'].avname)

@probe_app.task()
def probe_scan(frontend, scanid, filename):
    try:
        conf_ftp = config.probe_config['ftp_brain']
        (fd, tmpname) = tempfile.mkstemp()
        os.close(fd)
        with FtpTls(conf_ftp.host, conf_ftp.port, conf_ftp.username, conf_ftp.password) as ftps:
            ftps.download("{0}/{1}".format(frontend, scanid), filename, tmpname)
        results = mscan.scan(tmpname)
        os.remove(tmpname)
        return results
    except Exception as e:
        print "Exception has occured:{0}".format(e)
        raise probe_scan.retry(countdown=30, max_retries=5)

