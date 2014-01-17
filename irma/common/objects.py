from lib.irma.database.objects import DatabaseObject
import config.dbconfig as dbconfig

class AttributeDictionary(dict):
    """A dictionnary with object-like accessors"""

    __getattr__ = lambda obj, key: obj.get(key, None)
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class Machine(DatabaseObject):
    _dbname = dbconfig.DB_NAME
    _collection = dbconfig.COLL_MACHINE

    def __init__(self, dbname=None, _id=None, label=None, uuid=None, disks=None, ip=None, os_type=None, os_variant=None, master=None):
        if dbname:
            self._dbname = dbname
        self.label = label
        self.uuid = uuid
        self.disks = disks
        self.ip = ip
        self.manager_ip = None
        self.manager_type = None
        self.os_type = os_type
        self.os_variant = os_variant
        self.master = master
        super(Machine, self).__init__(_id=_id)

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
    _dbname = dbconfig.DB_NAME
    _collection = dbconfig.COLL_SCANINFO

    def __init__(self, dbname=None, _id=None):
        if dbname:
            self._dbname = dbname
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
    _collection = dbconfig.COLL_RESINFO

    def __init__(self, dbname=None, _id=None):
        if dbname:
            self._dbname = dbname
        self.probelist = []
        self.results = {}
        super(ScanResults, self).__init__(_id=_id)

class System(DatabaseObject):
    _dbname = dbconfig.ADMIN_DB_NAME
    _collection = dbconfig.COLL_SETUP

    def __init__(self, dbname=None, _id=None):
        if dbname:
            self._dbname = dbname
        self.nodes = []
        self.probes = []
        super(System, self).__init__(_id=_id)


class Node(DatabaseObject):
    _dbname = dbconfig.ADMIN_DB_NAME
    _collection = dbconfig.COLL_NODE

    def __init__(self, dbname=None, _id=None):
        if dbname:
            self._dbname = dbname
        self.name = None
        self.address = None
        super(Node, self).__init__(_id=_id)

class Probe(DatabaseObject):
    _dbname = dbconfig.ADMIN_DB_NAME
    _collection = dbconfig.COLL_PROBE

    def __init__(self, dbname=None, _id=None):
        if dbname:
            self._dbname = dbname
        self.name = None
        self.type = None
        super(Node, self).__init__(_id=_id)
