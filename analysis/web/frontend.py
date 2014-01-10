import re
import os
import celery
from bottle import route, request, default_app, run, static_file
from lib.irma.common.utils import IRMA_RETCODE_OK, IRMA_RETCODE_WARNING, IRMA_RETCODE_ERROR
from lib.irma.fileobject.handler import FileObject
from bson import ObjectId
from config.config import IRMA_TIMEOUT
from config.brainconfig import brain_celery

# ______________________________________________________________ RESPONSE FORMATTER

def response(code, info):
    return {"result":code, "info":info}

def error(info):
    return response(IRMA_RETCODE_ERROR, info)

def warning(info):
    return response(IRMA_RETCODE_WARNING, info)

def success(info):
    return response(IRMA_RETCODE_OK, info)

# ______________________________________________________________ SERVER ROOT

@route("/")
def svr_index():
    return success("This is irma-brain")
# ______________________________________________________________ API SCAN

def validid(scanid):
    # scanid is a str(ObjectId)
    return re.match(r'[0-9a-fA-F]{24}', scanid)

@route("/scan", method='POST')
def scan_new():
    """ send list of filename for scanning """
    # analyze parameters
    force = False
    if request.params['force'] == 'True':
        force = True
    sondelist = None
    if 'sonde' in request.params:
        sondelist = request.params['sonde'].split(',')

    # save file in db
    oids = {}
    for f in request.files:
        filename = os.path.basename(f)
        upfile = request.files.get(f)
        data = upfile.file.read()
        fobj = FileObject()
        new = fobj.save(data, filename)
        oids[fobj._id] = {"name": filename, "new": new}

    # launch new celery task
    scanid = str(ObjectId())
    brain_celery.send_task("brain.braintasks.scan", args=(scanid, oids, sondelist, force))
    return success({"scanid":scanid, "sondelist":sondelist})

@route("/scan/results/<scanid>", method='GET')
def scan_results(scanid):
    # Filter malformed scanid
    if not validid(scanid):
        return error("not a valid scanid")
    # Launch a synchronous task (blocking for max IRMA_TIMEOUT seconds)
    try:
        task = brain_celery.send_task("brain.braintasks.scan_result", args=[scanid])
        (status, res) = task.get(timeout=IRMA_TIMEOUT)
    except celery.exceptions.TimeoutError:
        return error("timeout")
    return response(status, res)

@route("/scan/progress/<scanid>", method='GET')
def scan_progress(scanid):
    # Filter malformed scanid
    if not validid(scanid):
        return error("not a valid scanid")
    # Launch a synchronous task (blocking for max IRMA_TIMEOUT seconds)
    try:
        task = brain_celery.send_task("brain.braintasks.scan_progress", args=[scanid])
        (status, res) = task.get(timeout=IRMA_TIMEOUT)
    except celery.exceptions.TimeoutError:
        return error("timeout")
    return response(status, res)


@route("/scan/cancel/<scanid>", method='GET')
def scan_cancel(scanid):
    # Filter malformed scanid
    if not validid(scanid):
        return error("not a valid scanid")
    # Launch a synchronous task (blocking for max IRMA_TIMEOUT seconds)
    try:
        task = brain_celery.send_task("brain.braintasks.scan_cancel", args=[scanid])
        (status, res) = task.get(timeout=IRMA_TIMEOUT)
    except celery.exceptions.TimeoutError:
        return error("timeout")
    return response(status, res)
# ______________________________________________________________ API STATUS

@route("/sonde_list")
def status():
    # Check active queues with a synchronous task (blocking for max IRMA_TIMEOUT seconds)
    try:
        task = brain_celery.send_task("brain.braintasks.sonde_list", args=[])
        (status, res) = task.get(timeout=IRMA_TIMEOUT)
    except celery.exceptions.TimeoutError:
        return error("timeout")
    return response(status, res)

# ______________________________________________________________ API EXPORT

@route('/download/<file_oid>')
def download(file_oid):
    """ retrieve a file previously sent to the brain """
    fobj = FileObject(_id=file_oid)
    return static_file(fobj.name, download=fobj.data)

# ______________________________________________________________ MAIN

application = default_app()

if __name__ == "__main__":
    run(host='0.0.0.0', port=8080)
