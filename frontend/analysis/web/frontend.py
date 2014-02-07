import re
import os
import celery
from bottle import route, request, default_app, run, response
from lib.irma.common.utils import IrmaFrontendReturn
from lib.irma.fileobject.handler import FileObject
from bson import ObjectId
from config.config import IRMA_TIMEOUT
from config.brainconfig import brain_celery
from config.adminconfig import admin_celery

# ______________________________________________________________ SERVER ROOT

@route("/")
def svr_index():
    """ hello world """
    return IrmaFrontendReturn.success("This is irma-brain")
# ______________________________________________________________ API SCAN

def validid(scanid):
    # scanid is a str(ObjectId)
    return re.match(r'[0-9a-fA-F]{24}', scanid)

@route("/scan", method='POST')
def scan_new():
    """ launch new scan with psoted list of files"""
    # analyze parameters
    force = False
    if request.params['force'] == 'True':
        force = True
    probelist = None
    if 'probe' in request.params:
        probelist = request.params['probe'].split(',')

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
    brain_celery.send_task("brain.braintasks.scan", args=(scanid, oids, probelist, force))
    return IrmaFrontendReturn.success({"scanid":scanid, "probelist":probelist})

@route("/scan/results/<scanid>", method='GET')
def scan_results(scanid):
    """ get all jobs results from scan specified """
    # Filter malformed scanid
    if not validid(scanid):
        return IrmaFrontendReturn.error("not a valid scanid")
    # Launch a synchronous task (blocking for max IRMA_TIMEOUT seconds)
    try:
        task = brain_celery.send_task("brain.braintasks.scan_result", args=[scanid])
        (status, res) = task.get(timeout=IRMA_TIMEOUT)
    except celery.exceptions.TimeoutError:
        return IrmaFrontendReturn.error("timeout")
    return IrmaFrontendReturn.response(status, res)

@route("/scan/progress/<scanid>", method='GET')
def scan_progress(scanid):
    """ get all jobs status from scan specified """
    # Filter malformed scanid
    if not validid(scanid):
        return IrmaFrontendReturn.error("not a valid scanid")
    # Launch a synchronous task (blocking for max IRMA_TIMEOUT seconds)
    try:
        task = brain_celery.send_task("brain.braintasks.scan_progress", args=[scanid])
        (status, res) = task.get(timeout=IRMA_TIMEOUT)
    except celery.exceptions.TimeoutError:
        return IrmaFrontendReturn.error("timeout")
    return IrmaFrontendReturn.response(status, res)


@route("/scan/cancel/<scanid>", method='GET')
def scan_cancel(scanid):
    """ cancel all active jobs from scan specified """
    # Filter malformed scanid
    if not validid(scanid):
        return IrmaFrontendReturn.error("not a valid scanid")
    # Launch a synchronous task (blocking for max IRMA_TIMEOUT seconds)
    try:
        task = brain_celery.send_task("brain.braintasks.scan_cancel", args=[scanid])
        (status, res) = task.get(timeout=IRMA_TIMEOUT)
    except celery.exceptions.TimeoutError:
        return IrmaFrontendReturn.error("timeout")
    return IrmaFrontendReturn.response(status, res)
# ______________________________________________________________ API STATUS

@route("/probe_list")
def status():
    """ Check active queues with a synchronous task (blocking for max IRMA_TIMEOUT seconds) """
    try:
        task = brain_celery.send_task("brain.braintasks.probe_list", args=[])
        (status, res) = task.get(timeout=IRMA_TIMEOUT)
    except celery.exceptions.TimeoutError:
        return IrmaFrontendReturn.error("timeout")
    return IrmaFrontendReturn.response(status, res)

# ______________________________________________________________ API EXPORT

@route('/download/<file_oid>')
def download(file_oid):
    """ retrieve a file previously sent to the brain """
    fobj = FileObject(_id=file_oid)
    response.headers['Content-disposition'] = 'attachment; filename="%s"' % fobj.name
    return fobj.data

# ______________________________________________________________ MAIN

application = default_app()

if __name__ == "__main__":
    run(host='0.0.0.0', port=8080)
