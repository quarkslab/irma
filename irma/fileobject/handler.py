from common.compat import timestamp
from irma.database.nosqlhandler import NoSQLDatabase
from bson import ObjectId
import hashlib


class FileObject(object):
    _uri = None
    _dbname = None
    _collection = None

    def __init__(self, dbname=None, id=None):
        if dbname:
            self._dbname = dbname
        self._dbfile = None
        self._creation_date = timestamp()
        if id:
            self._id = ObjectId(id)
            self.load()

    def _exists(self, hashvalue):
        db = NoSQLDatabase(self._dbname, self._uri)
        return db.exists_file(self._dbname, self._collection, hashvalue)

    def load(self):
        db = NoSQLDatabase(self._dbname, self._uri)
        self._dbfile = db.get_file(self._dbname, self._collection, self._id)

    def save(self, data, name):
        db = NoSQLDatabase(self._dbname, self._uri)
        hashvalue = hashlib.sha256(data).hexdigest()
        self._id = self._exists(hashvalue)
        if not self._id:
            self._id = db.put_file(self._dbname, self._collection, data, name, hashvalue, [])
            self.load()
            return True
        else:
            self.load()
            if name != self.name and name not in self.altnames:
                self.altnames = self.altnames + [name]
                self.update_altnames(self.altnames)
            return False

    def update_altnames(self, altnames):
        db = NoSQLDatabase(self._dbname, self._uri)
        db.update_file_altnames(self._dbname, self._collection, self._id, altnames)
        self.load()

    def update_data(self, data):
        db = NoSQLDatabase(self._dbname, self._uri)
        db.update_file_data(self._dbname, self._collection, self._id, data)
        self.load()

    @property
    def name(self):
        """Get the first seen filename"""
        return self._dbfile.filename

    @property
    def length(self):
        """Get file length"""
        return self._dbfile.length

    @property
    def upload_date(self):
        """Get file upload date"""
        return self._dbfile.upload_date

    @property
    def upload_date_timestamp(self):
        """Get the upload date has a timestamp"""
        return self._creation_date

    @property
    def hashvalue(self):
        """Get the hexdigest of filedata"""
        return self._dbfile.hashvalue

    @property
    def altnames(self):
        """Get the alternative filenames"""
        return self._dbfile.altnames

    @altnames.setter
    def altnames(self, value):
        """Append the alternative filenames if not already there"""
        if value not in self.altnames:
            self.update_altnames(value)
        return

    @property
    def data(self):
        """Get the file data"""
        return self._dbfile.read()

    @property
    def id(self):
        """Return str version of ObjectId"""
        if not self._id:
            return None
        else:
            return str(self._id)
