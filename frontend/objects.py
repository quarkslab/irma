import config.parser as config
from lib.common.compat import timestamp
from lib.irma.database.nosqlobjects import NoSQLDatabaseObject
from lib.irma.fileobject.handler import FileObject
from lib.irma.common.utils import IrmaScanStatus, IrmaLockMode

cfg_dburi = config.get_db_uri()
cfg_dbname = config.frontend_config['mongodb'].dbname
cfg_coll = config.frontend_config['collections']

class ScanInfo(NoSQLDatabaseObject):
    _uri = cfg_dburi
    _dbname = cfg_dbname
    _collection = cfg_coll.scan_info

    def __init__(self, dbname=None, **kwargs):
        if dbname:
            self._dbname = dbname
        self.user = None
        self.date = timestamp()
        self.oids = {}
        self.probelist = None
        self.status = IrmaScanStatus.created
        super(ScanInfo, self).__init__(**kwargs)

    def update_status(self, status):
        self.status = status
        self.update({'status':self.status})

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
            r = ScanResults(id=oid, mode=IrmaLockMode.read)
            if r.results:
                scanfile = ScanFile(id=oid)
                sha256 = scanfile.hashvalue
                res[sha256] = {}
                res[sha256]['filename'] = name
                res[sha256]['results'] = dict((probe, results) for (probe, results) in r.results.iteritems() if probe in self.probelist)
        return res

    @classmethod
    def has_lock_timed_out(cls, id):
        return super(ScanInfo, cls).has_lock_timed_out(id)

    @classmethod
    def is_lock_free(cls, id):
        return super(ScanInfo, cls).is_lock_free(id)

    @classmethod
    def find(cls, **kwargs):
        return super(ScanInfo, cls).find(**kwargs)


class ScanResults(NoSQLDatabaseObject):
    _uri = cfg_dburi
    _dbname = cfg_dbname
    _collection = cfg_coll.scan_results

    def __init__(self, dbname=None, **kwargs):
        if dbname:
            self._dbname = dbname
        self.probelist = []
        self.results = {}
        super(ScanResults, self).__init__(**kwargs)

    @classmethod
    def has_lock_timed_out(cls, id):
        return super(ScanResults, cls).has_lock_timed_out(id)

    @classmethod
    def is_lock_free(cls, id):
        return super(ScanResults, cls).is_lock_free(id)

    @classmethod
    def init_id(cls, id, **kwargs):
        return super(ScanResults, cls).init_id(id, **kwargs)

class ScanFile(FileObject):
    _uri = cfg_dburi
    _dbname = cfg_dbname
    _collection = cfg_coll.scan_files
