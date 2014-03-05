import config.parser as config
from lib.irma.database.nosqlobjects import NoSQLDatabaseObject
from lib.irma.fileobject.handler import FileObject
from lib.irma.common.utils import IrmaScanStatus
from datetime import datetime, timedelta
from multiprocessing import Lock

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

class IrmaLockError(Exception):
    pass

# index in list
LOCK = 0
EXPIRES = 1
# default expiration delay
DEFAULT_EXPIRE_S = 60

class IrmaLock(object):
    _debug = False

    def __init__(self):
        self._locks = {}

    def _exists(self, lock_id):
        return lock_id in self._locks

    def _is_expired(self, lock_id):
        return self._locks[lock_id][EXPIRES] < datetime.now()

    def acquire(self, lock_id, duration=DEFAULT_EXPIRE_S):
        if self._exists(lock_id):
            # if lock already exists check expires
            if self._is_expired(lock_id):
                self.release(lock_id)
        else:
            # Create new lock
            self._locks.update({lock_id:[None, None]})
            self._locks[lock_id][LOCK] = Lock()

        if not self._locks[lock_id][LOCK].acquire(False):
            # Already taken raise Error
            raise IrmaLockError("Lock {0} already taken".format(lock_id))

        # add new expires
        expires = datetime.now() + timedelta(seconds=duration)
        self._locks[lock_id][EXPIRES] = expires
        if self._debug: print "lock {0} acquired".format(lock_id)

    def release(self, lock_id):
        try:
            if self._debug: print "lock {0} released".format(lock_id)
            self._locks[lock_id][LOCK].release()
        except ValueError:
            pass
        except KeyError:
            pass
