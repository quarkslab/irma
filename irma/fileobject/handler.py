from config import dbconfig
from lib.irma.database.handler import Database
import hashlib


class FileObject(object):
    _uri = dbconfig.MONGODB
    _dbname = dbconfig.DB_NAME
    _collection = dbconfig.COLL_FS

    def __init__(self, dbname=None, _id=None):
        if dbname:
            self._dbname = dbname
        self._dbfile = None
        if _id:
            self._id = _id
            self.load()

    def _exists(self, hashvalue):
        db = Database(self._dbname, self._uri)
        return db.exists_file(self._dbname, self._collection, hashvalue)

    def load(self):
        db = Database(self._dbname, self._uri)
        self._dbfile = db.get_file(self._dbname, self._collection, self._id)

    def save(self, data, name):
        db = Database(self._dbname, self._uri)
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
        db = Database(self._dbname, self._uri)
        db.update_file_altnames(self._dbname, self._collection, self._id, altnames)
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
        """Get fiel length"""
        return self._dbfile.upload_date

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
