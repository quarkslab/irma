from irma.database.nosqlhandler import NoSQLDatabase
from bson import ObjectId


class FileObject(object):
    _uri_file = None
    _uri = None
    _dbname_file = None
    _dbname = None
    _collection_file = None
    _collection = None

    def __init__(self, dbname=None, id=None):
        if dbname:
            self._dbname = dbname
        self._dbfile = None
        if id:
            self._id = ObjectId(id)
            self.load()

    def _exists(self, hashvalue):
        db = NoSQLDatabase(self._dbname_file, self._uri_file)
        return db.exists_file(self._dbname_file, self._collection_file, hashvalue)

    def load(self, _id):
        self._id = _id
        super(FileObject, self).load(self._id)
        self._load_file()

    def _load_file(self):
        db = NoSQLDatabase(self._dbname_file, self._uri_file)
        self._dbfile = db.get_file(self._dbname, self._collection_file, self._dbfile_id)

    def save(self, data, name):
        db = NoSQLDatabase(self._dbname, self._uri)
        self._id = db.put_file(self._dbname, self._collection, data, name, '', [])

    @property
    def name(self):
        """Get the filename"""
        return self._dbfile.filename

    @property
    def length(self):
        """Get file length"""
        return self._dbfile_length

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
