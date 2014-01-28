from datetime import datetime
import config.dbconfig as dbconfig
from lib.irma.database.objects import DatabaseObject

class AttributeDictionary(dict):
    """A dictionnary with object-like accessors"""

    __getattr__ = lambda obj, key: obj.get(key, None)
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

class ScanStatus:
    init = 10
    launched = 11
    finished = 20
    cancelling = 30
    cancelled = 31

    label = {
             init:"scan created",
             launched:"scan launched",
             finished:"scan finished",
             cancelled:"scan cancelled"
    }

class ScanInfo(DatabaseObject):
    # TODO add date"
    # TODO add accounting
    _dbname = dbconfig.DB_NAME
    _collection = dbconfig.COLL_SCANINFO

    def __init__(self, dbname=None, _id=None):
        if dbname:
            self._dbname = dbname
        self.user = None
        self.date = datetime.now()
        self.oids = {}
        self.taskid = None
        self.probelist = []
        self.status = ScanStatus.init
        super(ScanInfo, self).__init__(_id=_id)

    def get_results(self):
        res = {}
        for (oid, name) in self.oids.items():
            r = ScanResults(_id=oid)
            res[name] = dict((k, v) for (k, v) in r.results.iteritems() if k in self.probelist)
        return res

class ScanResults(DatabaseObject):
    _dbname = dbconfig.DB_NAME
    _collection = dbconfig.COLL_SCANRES

    def __init__(self, dbname=None, _id=None):
        if dbname:
            self._dbname = dbname
        self.probelist = []
        self.results = {}
        super(ScanResults, self).__init__(_id=_id)

