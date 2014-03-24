from common.compat import timestamp
from irma.database.nosqlhandler import NoSQLDatabase
import hashlib
from irma.database.nosqlobjects import NoSQLDatabaseObject


class FileObject(NoSQLDatabaseObject):
    _uri_file = None
    _uri = None
    _dbname_file = None
    _dbname = None
    _collection_file = None
    _collection = None

    def __init__(self, dbname_file=None, dbname_metadata=None, id=None):
        if dbname_file:
            self._dbname_file = dbname_file
        if dbname_metadata:
            self._dbname = dbname_metadata
        self._dbfile_upload_time = 0
        self._dbfile = ''
        self._dbfile_id = 0
        self._dbfile_name = ''
        self._dbfile_altnames = []
        self._dbfile_hash = ''
        self._dbfile_length = 0

        self._transient_attributes.append('_dbfile')

        super(FileObject, self).__init__(id)

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
        hashvalue = hashlib.sha256(data).hexdigest()
        self._dbfile_id = self._exists(hashvalue)
        if not self._dbfile_id:
            self._dbfile_name = name
            self._dbfile_hash = hashvalue
            super(FileObject, self)._save()
            db = NoSQLDatabase(self._dbname_file, self._uri_file)
            self._dbfile_id = db.put_file(self._dbname_file, self._collection_file, data, name, hashvalue, [])
            self._dbfile_upload_time = timestamp()
            self._load_file()
            self._dbfile_length = self._dbfile.length
            self.update()
            return True
        else:
            if name != self._dbfile_name and name not in self._dbfile_altnames:
                self._dbfile_altnames = self._dbfile_altnames + [name]
                self.update_altnames(self._dbfile_altnames)
            return False

    def update_altnames(self, altnames):
        super(FileObject, self).update({'_altnames': altnames})

    def update_data(self, data):
        db = NoSQLDatabase(self._dbname, self._uri_file)
        if len(self._dbfile_altnames) == 0:
            db.remove(self._dbname, self._collection, self._dbfile_id)
        self.save(data, self._dbfile_name)

    @property
    def name(self):
        """Get the first seen filename"""
        return self._dbfile_name

    @property
    def length(self):
        """Get file length"""
        return self._dbfile_length

    @property
    def upload_date(self):
        """Get the upload date has a timestamp"""
        return self._dbfile_upload_time

    @property
    def hashvalue(self):
        """Get the hexdigest of filedata"""
        return self._dbfile_hash

    @property
    def altnames(self):
        """Get the alternative filenames"""
        return self._dbfile_altnames

    @altnames.setter
    def altnames(self, value):
        """Append the alternative filenames if not already there"""
        if value not in self.altnames:
            self._dbfile_altnames.append(value)
            self.update_altnames(self.altnames)
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
