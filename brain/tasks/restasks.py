from lib.irma.common.utils import IrmaTaskReturn
from celery import Celery
import config

results_app = Celery('restasks')
config.conf_results_celery(results_app)

# frontend_celery = Celery('frontend')
# config.conf_frontend_celery(frontend_celery)

@results_app.task()
def scan_result(frontend, scanid, filename, probe, result):
    print "{0}{1}{2}{3}->{4}".format(frontend, scanid, filename, probe, result)
    """
    s = ScanInfo(_id=scanid)
    return IrmaTaskReturn.success(s.get_results())
    """
    return IrmaTaskReturn.error("unknown")
