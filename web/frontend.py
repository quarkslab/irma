import re
import os
import celery
from celery import signature
from bottle import route, request, default_app, abort, run
from brain import braintasks, brainstorage
from config.dbconfig import SCAN_STATUS_INIT, SCAN_STATUS_LAUNCHED, SCAN_STATUS_FINISHED, SCAN_STATUS_CANCELLED
from bson import ObjectId

bstorage = brainstorage.BrainStorage()
brain_celery = celery.Celery('braintasks')
brain_celery.config_from_object('config.brainconfig')

sonde_celery = celery.Celery('sondetasks')
sonde_celery.config_from_object('config.sondeconfig')

@route("/")
def svr_index():
    return "This is irma-brain:\n"

# ______________________________________________________________ API SCAN

def validid(scanid):
    return re.match(r'[0-9a-fA-F]{24}', scanid)

@route("/scan", method='POST')
def scan_new():
    """ send list of filename for scanning """
    oids = {}
    for f in request.files:
        filename = os.path.basename(f)
        upfile = request.files.get(f)
        data = upfile.file.read()
        file_oid = bstorage.store_file(data, name=filename)
        oids[file_oid] = filename
    scanid = str(ObjectId())
    # s = signature("braintasks.scan", args=(scanid, oids))
    brain_celery.send_task("braintasks.scan", args=(scanid, oids))
    bstorage.update_scan_record(scanid, {'status':SCAN_STATUS_INIT, 'oids': oids, 'avlist':[]})
    return {"scanid":scanid}

@route("/scan/results/<scanid>", method='GET')
def scan_results(scanid):
    if not validid(scanid):
        return {"error": "not a valid scanid"}
    res = bstorage.get_scan_results(scanid)
    return {"result": res}

@route("/scan/progress/<scanid>", method='GET')
def scan_progress(scanid):
    if not validid(scanid):
        return {"result":"error", "info":"not a valid scanid"}
    status = bstorage.get_scan_status(scanid)
    if status == SCAN_STATUS_INIT:
        return {"result":"not ready", "info":"task not launched"}
    elif status == SCAN_STATUS_LAUNCHED:
        task_id = bstorage.get_scan_taskid(scanid)
        if not task_id:
            return {"result":"error", "info":"task_id not set"}
        job = sonde_celery.GroupResult.restore(task_id)
        if not job:
            return {"result":"error", "info":"not a valid taskid"}
        else:
            nbcompleted = nbsuccessful = 0
            for j in job:
                if j.ready(): nbcompleted += 1
                if j.successful(): nbsuccessful += 1
            return {"result": "in progress", "total":len(job), "finished":nbcompleted, "successful":nbsuccessful}
    elif status == SCAN_STATUS_FINISHED:
        return {"result":"finished"}
    elif status == SCAN_STATUS_CANCELLED:
        return {"result":"cancelled"}
    return {"result":"unknown status %d" % status}


@route("/scan/cancel/<scanid>", method='GET')
def scan_cancel(scanid):
    if not validid(scanid):
        return {"result":"error", "info":"not a valid scanid"}

    status = bstorage.get_scan_status(scanid)
    if status == SCAN_STATUS_INIT:
        return {"result":"not ready", "info":"task not launched"}
    elif status == SCAN_STATUS_LAUNCHED:
        task_id = bstorage.get_scan_taskid(scanid)
        job = sonde_celery.GroupResult.restore(task_id)
        if not job:
            return {"result":"error", "info":"not a valid taskid"}
        else:
            nbcompleted = nbcancelled = 0
            for j in job:
                if j.ready():
                    nbcompleted += 1
                else:
                    j.revoke(terminate=True)
                    nbcancelled += 1
            return {"result": "cancelling", "total":len(job), "finished":nbcompleted, "cancelled":nbcancelled}
    elif status == SCAN_STATUS_FINISHED:
        return {"result":"finished"}
    elif status == SCAN_STATUS_CANCELLED:
        return {"result":"cancelled"}
    return {"result":"unknown status %d" % status}
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
