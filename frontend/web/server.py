import re
import os
import celery
from bottle import route, request, default_app, run, response
from lib.irma.common.utils import IrmaFrontendReturn
from frontend.objects import ScanInfo, ScanFile
import config

cfg_timeout = config.get_brain_celery_timeout()

frontend_app = celery.Celery('frontendtasks')
config.conf_frontend_celery(frontend_app)

scan_app = celery.Celery('scantasks')
config.conf_brain_celery(scan_app)
# ______________________________________________________________ SERVER ROOT

@route("/")
def svr_index():
    """ hello world """
    return IrmaFrontendReturn.success("This is irma-brain")

# ______________________________________________________________ API SCAN

def validid(scanid):
    # scanid is a str(ObjectId)
    return re.match(r'[0-9a-fA-F]{24}', scanid)

@route("/scan/new")
def scan_new():
    try:
        si = ScanInfo()
        si.save()
        return IrmaFrontendReturn.success({"scanid":si.id})
    except Exception as e:
        return IrmaFrontendReturn.error(str(e))


@route("/scan/add/<scanid>", method='POST')
def scan_add(scanid):
    """ add one file to scan list for a specified scan id"""
    # Filter malformed scanid
    if not validid(scanid):
        return IrmaFrontendReturn.error("not a valid scanid")
    try:
        si = ScanInfo(id=scanid)
        # save file in db
        for f in request.files:
            upfile = request.files.get(f)
            filename = os.path.basename(upfile.filename)
            data = upfile.file.read()
            fobj = ScanFile()
            fobj.save(data, filename)
            si.oids[fobj.id] = filename
        return IrmaFrontendReturn.success({"scanid":scanid, "nb_files": len(si.oids)})
    except Exception as e:
        return IrmaFrontendReturn.error(str(e))

@route("/scan/launch/<scanid>", method='GET')
def scan_launch(scanid):
    # Filter malformed scanid
    if not validid(scanid):
        return IrmaFrontendReturn.error("not a valid scanid")

    try:
        si = ScanInfo(id=scanid)
        # analyze parameters
        force = False
        if request.params['force'] == 'True':
            force = True
        probelist = None
        if 'probe' in request.params:
            probelist = request.params['probe'].split(',')

        si.probelist = probelist
        # launch ftp upload via frontend task
        frontend_app.send_task("frontend.tasks.scan_launch", args=(si.id, si.oids, si.probelist, force))
        return IrmaFrontendReturn.success({"scanid":si.id, "probelist":si.probelist})
    except Exception as e:
        return IrmaFrontendReturn.error(str(e))

@route("/scan/results/<scanid>", method='GET')
def scan_results(scanid):
    """ get all jobs results from scan specified """
    # Filter malformed scanid
    if not validid(scanid):
        return IrmaFrontendReturn.error("not a valid scanid")
    try:
        # fetch results in db
        si = ScanInfo(id=scanid)
        return IrmaFrontendReturn.success(si.get_results())
    except Exception as e:
        return IrmaFrontendReturn.error(str(e))

@route("/scan/progress/<scanid>", method='GET')
def scan_progress(scanid):
    """ get all jobs status from scan specified """
    # Filter malformed scanid
    if not validid(scanid):
        return IrmaFrontendReturn.error("not a valid scanid")
    # Launch a synchronous task (blocking for max IRMA_TIMEOUT seconds)
    try:
        task = scan_app.send_task("brain.tasks.scan_progress", args=[scanid])
        (status, res) = task.get(timeout=cfg_timeout)
        return IrmaFrontendReturn.response(status, res)
    except celery.exceptions.TimeoutError:
        return IrmaFrontendReturn.error("timeout")
    except Exception as e:
        return IrmaFrontendReturn.error(str(e))


@route("/scan/cancel/<scanid>", method='GET')
def scan_cancel(scanid):
    """ cancel all active jobs from scan specified """
    # Filter malformed scanid
    if not validid(scanid):
        return IrmaFrontendReturn.error("not a valid scanid")
    # Launch a synchronous task (blocking for max IRMA_TIMEOUT seconds)
    try:
        task = scan_app.send_task("brain.tasks.scan_cancel", args=[scanid])
        (status, res) = task.get(timeout=cfg_timeout)
        return IrmaFrontendReturn.response(status, res)
    except celery.exceptions.TimeoutError:
        return IrmaFrontendReturn.error("timeout")
    except Exception as e:
        return IrmaFrontendReturn.error(str(e))
# ______________________________________________________________ API STATUS

@route("/probe_list")
def status():
    """ Check active queues with a synchronous task (blocking for max IRMA_TIMEOUT seconds) """
    try:
        task = scan_app.send_task("brain.tasks.probe_list", args=[])
        (status, res) = task.get(timeout=cfg_timeout)
        return IrmaFrontendReturn.response(status, res)
    except celery.exceptions.TimeoutError:
        return IrmaFrontendReturn.error("timeout")
    except Exception as e:
        return IrmaFrontendReturn.error(str(e))

# ______________________________________________________________ API EXPORT

@route('/download/<file_oid>')
def download(file_oid):
    """ retrieve a file previously sent to the brain """
    fobj = ScanFile(id=file_oid)
    response.headers['Content-disposition'] = 'attachment; filename="%s"' % fobj.name
    return fobj.data

# ______________________________________________________________ MAIN

application = default_app()

if __name__ == "__main__":
    run(host='0.0.0.0', port=8080)
