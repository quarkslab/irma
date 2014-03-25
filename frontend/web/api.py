import re, os
import bottle
from bottle import route, request, default_app, run

"""
    IRMA FRONTEND API
    defines all accessible route once the bottle server is up.
    To launch the server just type:

    $ python -m frontend.web.api

    it will launch the server on 0.0.0.0 port 8080

    For test purpose set DEBUG to True and launch, the server will use mockup core class
    irma dependencies are no more required.
"""

DEBUG = True
if DEBUG:
    from mucore import IrmaFrontendWarning, IrmaFrontendError, IrmaFrontendReturn
    import mucore as core
else:
    from lib.irma.common.utils import IrmaFrontendReturn
    from frontend.web.core import IrmaFrontendWarning, IrmaFrontendError
    import frontend.web.core as core

# ______________________________________________________________ SERVER TEST MODE

@bottle.error(405)
def method_not_allowed(res):
    """ allow CORS request for debug purpose """
    if request.method == 'OPTIONS':
        new_res = bottle.HTTPResponse()
        new_res.set_header('Access-Control-Allow-Origin', '*')
        return new_res
    res.headers['Allow'] += ', OPTIONS'
    return request.app.default_error_handler(res)

@bottle.hook('after_request')
def enableCORSAfterRequestHook():
    """ allow CORS request for debug purpose """
    bottle.response.set_header('Access-Control-Allow-Origin', '*')

# ______________________________________________________________ SERVER ROOT

@route("/")
def svr_index():
    """ hello world

    :route: /
    :rtype: dict of 'code': int, 'msg': str
    :return: on success 'code' is 0
    """
    return IrmaFrontendReturn.success()

# ______________________________________________________________ API SCAN

def validid(scanid):
    """ check scanid format - should be a str(ObjectId)"""
    return re.match(r'[0-9a-fA-F]{24}', scanid)

@route("/scan/new")
def scan_new():
    """ create new scan 
    
    :route: /scan/new
    :rtype: dict of 'code': int, 'msg': str [, optional 'scan_id':str]
    :return: 
        on success 'scan_id' contains the newly created scan id
        on error 'msg' gives reason message
    """
    try:
        scan_id = core.scan_new()
        return IrmaFrontendReturn.success(scan_id=scan_id)
    except IrmaFrontendWarning as e:
        return IrmaFrontendReturn.warning(str(e))
    except IrmaFrontendError as e:
        return IrmaFrontendReturn.error(str(e))
    except Exception as e:
        return IrmaFrontendReturn.error(str(e))


@route("/scan/add/<scanid>", method='POST')
def scan_add(scanid):
    """ add posted file(s) to the specified scan 
    
    :route: /scan/add/<scanid>
    :postparam: multipart form with filename(s) and file(s) data
    :param scanid: id returned by scan_new
    :note: files are posted as multipart/form-data
    :rtype: dict of 'code': int, 'msg': str [, optional 'nb_files':int]
    :return: 
        on success 'nb_files' total number of files for the scan
        on error 'msg' gives reason message
    """
    # Filter malformed scanid
    if not validid(scanid):
        return IrmaFrontendReturn.error("not a valid scanid")
    try:
        files = {}
        for f in request.files:
            upfile = request.files.get(f)
            filename = os.path.basename(upfile.filename)
            data = upfile.file.read()
            files[filename] = data
        nb_files = core.scan_add(scanid, files)
        return IrmaFrontendReturn.success(nb_files=nb_files)
    except IrmaFrontendWarning as e:
        return IrmaFrontendReturn.warning(str(e))
    except IrmaFrontendError as e:
        return IrmaFrontendReturn.error(str(e))
    except Exception as e:
        return IrmaFrontendReturn.error(str(e))

@route("/scan/launch/<scanid>", method='GET')
def scan_launch(scanid):
    """ launch specified scan 
    
    :route: /scan/launch/<scanid>
    :getparam: force=True or False
    :getparam: probe=probe1,probe2
    :param scanid: id returned by scan_new
    :rtype: dict of 'code': int, 'msg': str [, optional 'probe_list':list]
    :return: 
        on success 'probe_list' is the list of probes used for the scan
        on error 'msg' gives reason message
    """
    # Filter malformed scanid
    if not validid(scanid):
        return IrmaFrontendReturn.error("not a valid scanid")
    try:
        # handle 'force' parameter
        force = False
        if 'force' in request.params and request.params['force'] == 'True':
            force = True
        # handle 'probe' parameter
        in_probelist = None
        if 'probe' in request.params:
            in_probelist = request.params['probe'].split(',')
        out_probelist = core.scan_launch(scanid, force, in_probelist)
        return IrmaFrontendReturn.success(probe_list=out_probelist)
    except IrmaFrontendWarning as e:
        return IrmaFrontendReturn.warning(str(e))
    except IrmaFrontendError as e:
        return IrmaFrontendReturn.error(str(e))
    except Exception as e:
        return IrmaFrontendReturn.error(str(e))

@route("/scan/result/<scanid>", method='GET')
def scan_result(scanid):
    """ get all results from files of specified scan 
    
    :route: /scan/result/<scanid>
    :param scanid: id returned by scan_new
    :rtype: dict of 'code': int, 'msg': str [, optional 'scan_results': dict of [sha256 value: dict of 'filenames':list of filename, 'results': dict of [str probename: dict [results of probe]]]]
    :return: 
        on success 'scan_results' is the dict of results for each filename
        on error 'msg' gives reason message
    """
    # Filter malformed scanid
    if not validid(scanid):
        return IrmaFrontendReturn.error("not a valid scanid")
    try:
        results = core.scan_results(scanid)
        return IrmaFrontendReturn.success(scan_results=results)
    except IrmaFrontendWarning as e:
        return IrmaFrontendReturn.warning(str(e))
    except IrmaFrontendError as e:
        return IrmaFrontendReturn.error(str(e))
    except Exception as e:
        return IrmaFrontendReturn.error(str(e))

@route("/scan/progress/<scanid>", method='GET')
def scan_progress(scanid):
    """ get scan progress for specified scan
    
    :route: /scan/progress/<scanid>
    :param scanid: id returned by scan_new
    :rtype: dict of 'code': int, 'msg': str [, optional 'progress_details': total':int, 'finished':int, 'successful':int]
    :return: 
        on success 'progress_details' contains informations about submitted jobs by irma-brain
        on warning 'msg' gives scan status that does not required progress_details like 'processed' or 'finished'
        on error 'msg' gives reason message
    """
    # Filter malformed scanid
    if not validid(scanid):
        return IrmaFrontendReturn.error("not a valid scanid")
    try:
        progress = core.scan_progress(scanid)
        return IrmaFrontendReturn.success(progress_details=progress)
    except IrmaFrontendWarning as e:
        return IrmaFrontendReturn.warning(str(e))
    except IrmaFrontendError as e:
        return IrmaFrontendReturn.error(str(e))
    except Exception as e:
        return IrmaFrontendReturn.error(str(e))


@route("/scan/cancel/<scanid>", method='GET')
def scan_cancel(scanid):
    """ cancel all remaining jobs for specified scan
    
    :route: /scan/cancel/<scanid>
    :param scanid: id returned by scan_new
    :rtype: dict of 'code': int, 'msg': str [, optional 'cancel_details': total':int, 'finished':int, 'cancelled':int]
    :return: 
        on success 'cancel_details' contains informations about cancelled jobs by irma-brain
        on warning 'msg' gives scan status that make it not cancellable
        on error 'msg' gives reason message
    """
    # Filter malformed scanid
    if not validid(scanid):
        return IrmaFrontendReturn.error("not a valid scanid")
    try:
        cancel = core.scan_cancel(scanid)
        return IrmaFrontendReturn.success(cancel_details=cancel)
    except IrmaFrontendWarning as e:
        return IrmaFrontendReturn.warning(str(e))
    except IrmaFrontendError as e:
        return IrmaFrontendReturn.error(str(e))
    except Exception as e:
        return IrmaFrontendReturn.error(str(e))
# ______________________________________________________________ API STATUS

@route("/probe/list")
def probe_list():
    """ get active probe list
    
    :route: /probe/list
    :rtype: dict of 'code': int, 'msg': str [, optional 'probe_list': list of str]
    :return: 
        on success 'probe_list' contains list of probes names
        on error 'msg' gives reason message
    """
    try:
        probelist = core.probe_list()
        return IrmaFrontendReturn.success(probe_list=probelist)
    except IrmaFrontendWarning as e:
        return IrmaFrontendReturn.warning(str(e))
    except IrmaFrontendError as e:
        return IrmaFrontendReturn.error(str(e))
    except Exception as e:
        return IrmaFrontendReturn.error(str(e))

# ______________________________________________________________ MAIN

application = default_app()

if __name__ == "__main__":
    print "Irma Web Api",
    if DEBUG: print " /!\\ Debug MODE /!\\"
    run(host='0.0.0.0', port=8080)
