import re
import os
import celery
from celery import signature
from bottle import route, request, default_app, run
from brain import brainstorage
from config.dbconfig import SCAN_STATUS_INIT, SCAN_STATUS_LAUNCHED, SCAN_STATUS_FINISHED, SCAN_STATUS_CANCELLED
from bson import ObjectId
from config.config import IRMA_TIMEOUT

bstorage = brainstorage.BrainStorage()
brain_celery = celery.Celery('braintasks')
brain_celery.config_from_object('config.brainconfig')

@route("/")
def svr_index():
    return "This is irma-brain:\n"

# ______________________________________________________________ API SCAN

def validid(scanid):
    # scanid is a str(ObjectId)
    return re.match(r'[0-9a-fA-F]{24}', scanid)

@route("/scan", method='POST')
def scan_new():
    """ send list of filename for scanning """
    oids = {}
    for f in request.files:
        filename = os.path.basename(f)
        upfile = request.files.get(f)
        data = upfile.file.read()
        (new, file_oid) = bstorage.store_file(data, name=filename)
        oids[file_oid] = {"name": filename, "new": new}
    scanid = str(ObjectId())
    brain_celery.send_task("brain.braintasks.scan", args=(scanid, oids))
    return {"scanid":scanid}

@route("/scan/results/<scanid>", method='GET')
def scan_results(scanid):
    # Filter malformed scanid
    if not validid(scanid):
        return {"error": "not a valid scanid"}
    res = bstorage.get_scan_results(scanid)
    return {"result": res}

@route("/scan/progress/<scanid>", method='GET')
def scan_progress(scanid):
    # Filter malformed scanid
    if not validid(scanid):
        return {"result":"error", "info":"not a valid scanid"}
    # Launch a synchronous task (blocking for max IRMA_TIMEOUT seconds)
    try:
        task = brain_celery.send_task("brain.braintasks.scan_progress", args=[scanid])
        res = task.get(timeout=IRMA_TIMEOUT)
    except celery.exceptions.TimeoutError:
        return {"result":"error", "info":"timeout"}
    return res


@route("/scan/cancel/<scanid>", method='GET')
def scan_cancel(scanid):
    # Filter malformed scanid
    if not validid(scanid):
        return {"result":"error", "info":"not a valid scanid"}
    # Launch a synchronous task (blocking for max IRMA_TIMEOUT seconds)
    try:
        task = brain_celery.send_task("brain.braintasks.scan_cancel", args=(scanid))
        res = task.get(timeout=IRMA_TIMEOUT)
    except celery.exceptions.TimeoutError:
        return {"result":"error", "info":"timeout"}
    return res
# ______________________________________________________________ API STATUS

@route("/status")
def status():
    return {"result": "TODO"}

# ______________________________________________________________ API EXPORT

def export(filename, oid):
    """ retrieve a file previously sent to the brain """
    return {"result": "TODO"}

# ______________________________________________________________ MAIN

application = default_app()

if __name__ == "__main__":
    run(host='0.0.0.0', port=8080)
