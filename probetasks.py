import importlib
from config.probeconfig import probe_celery
from lib.irma.common.objects import ScanResults
from lib.irma.fileobject.handler import FileObject
from config.config import AVNAME

mscan = importlib.import_module("probe." + AVNAME)

@probe_celery.task()
def probe_scan(scan_oid, file_oid):
    sfile = FileObject(_id=file_oid)
    scan_results = mscan.scan(sfile)
    r = ScanResults(_id=file_oid)
    if AVNAME not in r.probelist:
        r.probelist.append(AVNAME)
        r.results.update({AVNAME:scan_results})
    return {'scan_oid':scan_oid, 'file_oid': file_oid, 'avname': AVNAME}

