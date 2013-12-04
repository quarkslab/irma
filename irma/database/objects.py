import config.dbconfig as dbconfig
from handler import Database

class DatabaseObjectList(object):
    #TODO derived class from UserList to handle list of databaseobject, group remove, group update...
    pass
    
class DatabaseObject(object):
    dbname      = None
    collection  = None 
    
    def __init__(self, _id = None):
        self._id = _id
        if self._id:
            self.load(self._id)

    # TODO: Add support for both args and kwargs
    def from_dict(self, dict_object):
        for k, v in dict_object.items():
            setattr(self, k, v)

    # See http://stackoverflow.com/questions/1305532/ to handle it in a generic way
    def to_dict(self):
        """Converts object to dict.
        @return: dict
        """
        # from http://stackoverflow.com/questions/61517/python-dictionary-from-an-objects-fields
        return dict((key, getattr(self, key)) for key in dir(self) if key not in dir(self.__class__) and getattr(self,key) is not None)

    def save(self):
        db = Database(dbconfig.DB_NAME,dbconfig.MONGODB)
        print "Save in dbname %s, collection %s"%(self.dbname,self.collection)
        self._id = db.save(self.dbname, self.collection, self.to_dict())
        return 
    
    def load(self, _id):
        self._id = _id
        db = Database(dbconfig.DB_NAME,dbconfig.MONGODB)
        dict_object = db.load(self.dbname, self.collection,self._id) 
        self.from_dict(dict_object)
        return
    
    def remove(self):
        db = Database(dbconfig.DB_NAME,dbconfig.MONGODB)
        db.remove(self.dbname, self.collection, self._id)
        return
       
        
class Machine(DatabaseObject):
    dbname      = dbconfig.DB_NAME
    collection  = dbconfig.COLL_MACHINE 
    
    def __init__(self, _id=None, label=None, uuid=None, disks=None, ip=None, os_type=None, os_variant=None, master=None):
        self.label=label
        self.uuid=uuid
        self.disks=disks
        self.ip=ip
        self.manager_ip=None
        self.manager_type=None
        self.os_type=os_type
        self.os_variant=os_variant
        self.master=master
        super(Machine, self).__init__(_id=_id)
        
    """def set_manager(self, spec, mm_ip, mm_type):
            # get table descriptor and update
            machines_tbl = self._table(self._db_name, self._machine_table_name)
            try:
                machines_tbl.update(spec, {"$set": {"manager_ip": mm_ip,
                                                    "manager_type": mm_type}})
            except Exception as e:
                raise IrmaDatabaseError("{0}".format(e))
    """

class ScanInfo(DatabaseObject):
    dbname      = dbconfig.DB_NAME
    collection  = dbconfig.COLL_SCANINFO
    
    def __init__(self, scanid=None, oids=[], taskid=None, avlist=[]):
        self.oids   = oids
        self.taskid = taskid
        self.avlist = avlist
        self.status = dbconfig.SCAN_STATUS_INIT
        super(ScanInfo,self).__init__(_id=scanid)
                    
class ScanResults(DatabaseObject):
    dbname      = dbconfig.DB_NAME
    collection  = dbconfig.COLL_RESINFO
    
    def __init__(self, resid=None, oids=[], taskid=None, avlist=[]):
        self.oids   = oids
        self.taskid = taskid
        self.avlist = avlist
        self.status = dbconfig.SCAN_STATUS_INIT
        super(ScanResults,self).__init__(_id=resid)
        
