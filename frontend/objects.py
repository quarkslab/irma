import config
from lib.irma.database.nosqlobjects import NoSQLDatabaseObject
from lib.irma.fileobject.handler import FileObject
from lib.irma.common.utils import IrmaScanStatus
from datetime import datetime

cfg_dburi = config.get_db_uri()
cfg_dbname = config.frontend_config['mongodb'].dbname
cfg_coll = config.frontend_config['collections']

class ScanInfo(NoSQLDatabaseObject):
    _uri = cfg_dburi
    _dbname = cfg_dbname
    _collection = cfg_coll.scan_info

    def __init__(self, dbname=None, id=None):
        if dbname:
            self._dbname = dbname
        self.user = None
        self.date = datetime.now()
        self.oids = {}
        self.probelist = None
        self.status = IrmaScanStatus.created
        super(ScanInfo, self).__init__(id=id)

    def is_launchable(self):
        return self.status == IrmaScanStatus.created

    def is_launched(self):
        return self.status == IrmaScanStatus.launched

    def launched(self):
        self.status = IrmaScanStatus.launched

    def processed(self):
        self.status = IrmaScanStatus.processed

    def cancelled(self):
        self.status = IrmaScanStatus.cancelled

    def finished(self):
        self.status = IrmaScanStatus.finished

    def is_completed(self):
        probelist = self.probelist
        for fileinfo in self.oids.values():
            remaining = [probe for probe in probelist if probe not in fileinfo['probedone']]
            if len(remaining) != 0:
                # at least one result is not there
                return False
        return True

    def get_results(self):
        res = {}
        for (oid, info) in self.oids.items():
            name = info['name']
            r = ScanResults(id=oid)
            if r.results:
                scanfile = ScanFile(id=oid)
                sha256 = scanfile.hashvalue
                res[sha256] = {}
                res[sha256]['filename'] = name
                res[sha256]['results'] = dict((probe, results) for (probe, results) in r.results.iteritems() if probe in self.probelist)
        return res

class ScanResults(NoSQLDatabaseObject):
    _uri = cfg_dburi
    _dbname = cfg_dbname
    _collection = cfg_coll.scan_results

    def __init__(self, dbname=None, id=None):
        if dbname:
            self._dbname = dbname
        self.probelist = []
        self.results = {}
        super(ScanResults, self).__init__(id=id)

class ScanFile(FileObject):
    _uri = cfg_dburi
    _dbname = cfg_dbname
    _collection = cfg_coll.scan_files
