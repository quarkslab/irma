import requests
import json
from marshmallow import fields, Schema

# Warning this is a copy of IrmaScanStatus lib.irma.common.utils
# in order to get rid of this dependency
# KEEP SYNCHRONIZED


class IrmaScanStatus:
    empty = 0
    ready = 10
    uploaded = 20
    launched = 30
    processed = 40
    finished = 50
    flushed = 60
    # cancel
    cancelling = 100
    cancelled = 110
    # errors
    error = 1000
    # Probes 101x
    error_probe_missing = 1010
    error_probe_na = 1011
    # FTP 102x
    error_ftp_upload = 1020

    label = {empty: "empty",
             ready: "ready",
             uploaded: "uploaded",
             launched: "launched",
             processed: "processed",
             finished: "finished",
             cancelling: "cancelling",
             cancelled: "cancelled",
             flushed: "flushed",
             error: "error",
             error_probe_missing: "probelist missing",
             error_probe_na: "probe(s) not available",
             error_ftp_upload: "ftp upload error"
             }


class IrmaError(Exception):
    """Error on cli script"""
    pass


class IrmaApiClient(object):

    def __init__(self, url, verbose=False):
        self.url = url
        self.verbose = verbose

    def get_call(self, route):
        resp = requests.get(self.url + route)
        return self._handle_resp(resp)

    def post_call(self, route, **extra_args):
        resp = requests.post(self.url + route, **extra_args)
        return self._handle_resp(resp)

    def _handle_resp(self, resp):
        if self.verbose:
            print "http code : {0}".format(resp.status_code)
            print "content : {0}".format(resp.content)
        if resp.status_code == 200:
            return json.loads(resp.content)
        else:
            reason = "Error {0}".format(resp.status_code)
            try:
                data = json.loads(resp.content)
                if 'message' in data and data['message'] is not None:
                    reason += ": {0}".format(data['message'])
            except:
                pass
            raise IrmaError(reason)


class IrmaProbesApi(object):

    def __init__(self, apiclient):
        self._apiclient = apiclient
        return

    def list(self):
        route = '/probes'
        return self._apiclient.get_call(route)


class IrmaScanApi(object):

    def __init__(self, apiclient):
        self._apiclient = apiclient
        self._scan_schema = IrmaScanSchema()
        self._results_schema = IrmaResultsSchema()
        return

    def new(self):
        route = '/scans'
        data = self._apiclient.post_call(route)
        return self._scan_schema.make_object(data)

    def get(self, scan_id):
        route = '/scans/{0}'.format(scan_id)
        data = self._apiclient.get_call(route)
        return self._scan_schema.make_object(data)

    def add(self, scan_id, filelist):
        postfiles = dict(map(lambda t: (t, open(t, 'rb')), filelist))
        route = '/scans/{0}/files'.format(scan_id)
        data = self._apiclient.post_call(route, files=postfiles)
        return self._scan_schema.make_object(data)

    def launch(self, scan_id, force, probe=None):
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        params = {'force': force}
        if probe is not None:
            params['probes'] = ','.join(probe)
        route = "/scans/{0}/launch".format(scan_id)
        data = self._apiclient.post_call(route,
                                         data=json.dumps(params),
                                         headers=headers)
        return self._scan_schema.make_object(data)

    def cancel(self, scan_id):
        route = '/scans/{0}/cancel'.format(scan_id)
        data = self._apiclient.post_call(route)
        return self._scan_schema.make_object(data)

    def result(self, scan_id):
        route = '/scans/{0}/results'.format(scan_id)
        data = self._apiclient.get_call(route)
        return self._scan_schema.make_object(data)

    def file_results(self, result_id):
        route = '/results/{0}'.format(result_id)
        data = self._apiclient.get_call(route)
        return self._results_schema.make_object(data)


# =============
#  Deserialize
# =============


class IrmaFileInfoSchema(Schema):
    class Meta:
        fields = ('size', 'sha1', 'timestamp_first_scan',
                  'timestamp_last_scan', 'sha256', 'id', 'md5', 'mimetype')

    def make_object(self, data):
        return IrmaFileInfo(**data)


class IrmaFileInfo(object):
    def __init__(self, size, sha1, timestamp_first_scan,
                 timestamp_last_scan, sha256, id, md5, mimetype):
        self.size = size
        self.sha1 = sha1
        self.timestamp_first_scan = timestamp_first_scan
        self.timestamp_last_scan = timestamp_last_scan
        self.sha256 = sha256
        self.id = id
        self.md5 = md5
        self.mimetype = mimetype

    def __repr__(self):
        ret = "Size: {0}\n".format(self.size)
        ret += "Sha1: {0}\n".format(self.sha1)
        ret += "Sha256: {0}\n".format(self.sha256)
        ret += "Md5: {0}s\n".format(self.md5)
        ret += "First Scan: {0}\n".format(self.timestamp_first_scan)
        ret += "Last Scan: {0}\n".format(self.timestamp_last_scan)
        ret += "Id: {0}\n".format(self.id)
        return ret

    def raw(self):
        return IrmaFileInfoSchema()


class IrmaProbeResult(object):

    def __init__(self, status, name, version, type, results=None,
                 error=None, duration=0, external_url=None,
                 uploaded_files=None):
        self.status = status
        self.name = name
        self.results = results
        self.version = version
        self.duration = duration
        self.type = type
        self.error = error
        self.external_url = external_url
        self.uploaded_files = uploaded_files

    def to_json(self):
        return IrmaProbeResultSchema().dumps(self).data

    def __str__(self):
        ret = "RetCode: {0}\n".format(self.status)
        ret += "ProbeName: {0}\n".format(self.name)
        ret += "Version: {0}\n".format(self.version)
        ret += "Duration: {0}s\n".format(self.duration)
        ret += "Category: {0}\n".format(self.type)
        if self.error is not None:
            ret += "Error: {0}\n".format(self.error)
        ret += "Results: {0}\n".format(self.results)
        if self.external_url is not None:
            ret += "External URL: {0}".format(self.external_url)
        if self.uploaded_files is not None:
            files = ", ".join(self.uploaded_files.keys())
            ret += "Uploaded Files: {0}".format(files)
        return ret


class IrmaProbeResultSchema(Schema):
    class Meta:
        fields = ('status', 'name', 'results', 'version',
                  'duration', 'type', 'error')

    def make_object(self, data):
        return IrmaProbeResult(**data)


class IrmaResults(object):
    def __init__(self, status, probes_finished, scan_id, name,
                 probes_total, result_id, file_sha256, parent_file_sha256,
                 file_infos=None, probe_results=None):
        self.status = status
        self.probes_finished = probes_finished
        self.scan_id = scan_id
        self.name = name
        self.file_sha256 = file_sha256
        self.parent_file_sha256 = parent_file_sha256
        self.probe_results = []
        if probe_results is not None:
            for pres in probe_results:
                pobj = IrmaProbeResultSchema().make_object(pres)
                self.probe_results.append(pobj)
        else:
            self.probe_results = None
        self.probes_total = probes_total
        if file_infos is not None:
            self.file_infos = IrmaFileInfoSchema().make_object(file_infos)
        else:
            self.file_infos = None
        self.result_id = result_id

    def to_json(self):
        return IrmaResultsSchema().dumps(self).data

    def __str__(self):
        ret = "Scanid: {0}\n".format(self.scan_id)
        ret += "Filename: {0}\n".format(self.name)
        ret += "ParentFile SHA256: {0}\n".format(self.parent_file_sha256)
        ret += "FileInfo: \n{0}\n".format(self.file_infos)
        ret += "Status: {0}\n".format(self.status)
        ret += "Probes finished: {0}\n".format(self.probes_finished)
        ret += "Probes Total: {0}\n".format(self.probes_total)
        ret += "Results: {0}\n".format(self.probe_results)
        return ret


class IrmaResultsSchema(Schema):
    probe_results = fields.Nested(IrmaProbeResultSchema, many=True)
    file_infos = fields.Nested(IrmaFileInfoSchema)

    class Meta:
        fields = ('status', 'probes_total', 'probes_finished', 'scan_id',
                  'name', 'result_id')

    def make_object(self, data):
        return IrmaResults(**data)


class IrmaScan(object):
    def __init__(self, status, probes_finished,
                 probes_total, date, id,
                 force, resubmit_files, mimetype_filtering,
                 results=[]):
        self.status = status
        self.probes_finished = probes_finished
        self.results = []
        if len(results) > 0:
            schema = IrmaResultsSchema()
            for r in results:
                self.results.append(schema.make_object(r))
        self.probes_total = probes_total
        self.date = date
        self.id = id
        self.force = force
        self.resubmit_files = resubmit_files
        self.mimetype_filtering = mimetype_filtering

    def is_launched(self):
        return self.status == IrmaScanStatus.launched

    def is_finished(self):
        return self.status == IrmaScanStatus.finished

    @property
    def pstatus(self):
        return IrmaScanStatus.label[self.status]

    def __repr__(self):
        ret = "Scanid: {0}\n".format(self.id)
        ret += "Status: {0}\n".format(self.pstatus)
        ret += "Options: Force [{0}] ".format(self.force)
        ret += "Mimetype [{0}] ".format(self.mimetype_filtering)
        ret += "Resubmit [{0}]\n".format(self.resubmit_files)
        ret += "Probes finished: {0}\n".format(self.probes_finished)
        ret += "Probes Total: {0}\n".format(self.probes_total)
        ret += "Results: {0}\n".format(self.results)
        ret += "Date: {0}\n".format(self.date)
        return ret


class IrmaScanSchema(Schema):
    results = fields.Nested(IrmaResultsSchema, many=True)

    class Meta:
        fields = ('status', 'probes_finished', 'date',
                  'probes_total', 'date', 'id', 'force',
                  'resumbit_files', 'mimetype_filtering')

    def make_object(self, data):
        return IrmaScan(**data)
