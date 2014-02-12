from handler import Database
from bson import ObjectId

class DatabaseObjectList(object):
    # TODO derived class from UserList to handle list of databaseobject, group remove, group update...
    pass

class DatabaseObject(object):
    """ Generic class to map an object to a db entry
    load will create an object from a db entry
    save will create/update a db entry with object's values"""
    _uri = None
    _dbname = None
    _collection = None

    def __init__(self, _id=None):
        self._id = ObjectId(_id)
        if self._id:
            self.load(self._id)

    def __del__(self):
        self.save()

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
        return dict((key, getattr(self, key)) for key in dir(self) if key not in dir(self.__class__) and getattr(self, key) is not None)

    def save(self):
        db = Database(self._dbname, self._uri)
        self._id = db.save(self._dbname, self._collection, self.to_dict())
        return

    def load(self, _id):
        self._id = _id
        db = Database(self._dbname, self._uri)
        dict_object = db.load(self._dbname, self._collection, self._id)
        # dict_object could be empty if we init a dbobject with a given id
        if dict_object:
            self.from_dict(dict_object)
        return

    def remove(self):
        db = Database(self._dbname, self._uri)
        db.remove(self._dbname, self._collection, self._id)
        return

    @property
    def id(self):
        """Return str version of ObjectId"""
        return str(self._id)

