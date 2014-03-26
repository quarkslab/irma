from irma.database.nosqlhandler import NoSQLDatabase
from bson import ObjectId


class FileObject(object):
    _uri = None
    _dbname = None
    _collection = None

    def __init__(self, dbname=None, id=None):
        if dbname:
            self._dbname = dbname
        self._dbfile = None
        if id:
            self._id = ObjectId(id)
            self.load()

    def load(self):
        db = NoSQLDatabase(self._dbname, self._uri)
        self._dbfile = db.get_file(self._dbname, self._collection, self._id)

    def save(self, data, name):
        db = NoSQLDatabase(self._dbname, self._uri)
        self._id = db.put_file(self._dbname, self._collection, data, name)

    def delete(self):
        db = NoSQLDatabase(self._dbname, self._uri)
        db.remove(self._dbname, self._collection, self._id)

    @property
    def data(self):
        """Get the data"""
        return self._dbfile.read()

    @property
    def id(self):
        """Return str version of ObjectId"""
        if not self._id:
            return None
        else:
            return str(self._id)
