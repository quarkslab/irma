#
# Copyright (c) 2013-2014 QuarksLab.
# This file is part of IRMA project.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License in the top-level directory
# of this distribution and at:
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# No part of the project, including this file, may be copied,
# modified, propagated, or distributed except according to the
# terms contained in the LICENSE file.

from ...common.compat import timestamp
from nosqlhandler import NoSQLDatabase
from bson import ObjectId
from bson.errors import InvalidId
from ..common.exceptions import IrmaDatabaseError, IrmaValueError


class NoSQLDatabaseObjectList(object):
    # TODO derived class from UserList to handle list of
    # databaseobject, group remove, group update...
    pass


class NoSQLDatabaseObject(object):
    """ Generic class to map an object to a db entry
    load will create an object from a db entry
    _save will create/update a db entry with object's values"""
    _uri = None
    _dbname = None
    _collection = None

    # List of transient attributes of the class (see to_dict)
    _transient_attributes = [
        '_transient_attributes',
        '_temp_id',
        '_is_instance_transient'
    ]

    def __init__(self, id=None, save=True):
        """ Constructor. Note: the object is being saved
        during the creation process.
        :param id: the id of the object to load
        :param save: if the object has to be saved, use only for temporary
            objects (you'll not be able to save it after the instantiation)
        :raise: IrmaDatabaseError, IrmaLockError, IrmaValueError
        """
        if type(self) is NoSQLDatabaseObject:
            reason = "The NoSQLDatabaseObject class has to be overloaded"
            raise IrmaValueError(reason)
        # transient (see _transient_attributes and to_dict)
        self._is_instance_transient = not save

        # create a new object or load an existing one with id
        # raise IrmaDatabaseError on loading invalid id
        self._id = None
        self._temp_id = None
        if id:
            try:
                self._id = ObjectId(id)
                # transient (see _transient_attributes and to_dict)
                self._temp_id = self._id
                self.load(self._id)
            except InvalidId as e:
                raise IrmaDatabaseError("{0}".format(e))
        elif save:
                self._save()

    # TODO: Add support for both args and kwargs
    def from_dict(self, dict_object):
        for k, v in dict_object.items():
            setattr(self, k, v)

    # See http://stackoverflow.com/questions/1305532/
    # to handle it in a generic way
    def to_dict(self):
        """Converts object to dict.
        :rtype: dict
        """
        # from stackoverflow.com/questions/61517/
        res = {}
        for key in dir(self):
            if key not in dir(self.__class__) and \
               getattr(self, key) is not None and \
               key not in self._transient_attributes:
                res[key] = getattr(self, key)
        return res

    def update(self, update_dict={}):
        """Update the current instance in the db, be sure to have the lock on
        the object before updating (ne verifications are being made)
        :param update_dict: the attributes/values to update in the bd,
            the whole object is being updated if nothing is provided
        :rtype: None
        """

        db = NoSQLDatabase(self._dbname, self._uri)
        # if the id is being changed, create a new instance
        if self._id != self._temp_id:
            old_id = self._temp_id
            self._temp_id = self._id
            self._save()
            db.remove(self._dbname, self._collection, old_id)
        else:
            if update_dict == {}:
                update_dict = self.to_dict()
                del update_dict['_id']
            db.update(self._dbname, self._collection, self._id, update_dict)
        return

    def _save(self):
        db = NoSQLDatabase(self._dbname, self._uri)
        self._id = db.save(self._dbname, self._collection, self.to_dict())
        self._temp_id = self._id
        return

    def load(self, _id):
        self._id = _id
        db = NoSQLDatabase(self._dbname, self._uri)
        dict_object = db.load(self._dbname, self._collection, self._id)
        # dict_object could be empty if we init a dbobject with a given id
        if dict_object:
            self.from_dict(dict_object)
            self._temp_id = self._id
        else:
            raise IrmaDatabaseError("id not present in collection")
        return

    def remove(self):
        db = NoSQLDatabase(self._dbname, self._uri)
        db.remove(self._dbname, self._collection, self._id)
        return

    @classmethod
    def get_temp_instance(cls, id):
        """Return a transient instance of the object
        corresponding to the given id
        :param id: the id of the object to return
        :rtype: NoSQLDatabaseObject
        :return: The transient object
        :raise: NotImplementedError if called from the mother class
        """
        if cls is NoSQLDatabaseObject:
            reason = "get_temp_instance must be overloaded in the subclasses"
            raise NotImplementedError(reason)
        return cls(id=id, save=False)

    @classmethod
    def find(cls, *args, **kwargs):
        """Return a list of all element from the collection that fit the query
        :param **kwargs: the parameters of the query
        :rtype: cursor
        :return: The objects that fit the query
        :raise: NotImplementedError if called from the mother class
        """
        if cls is NoSQLDatabaseObject:
            reason = "find must be overloaded in the subclasses"
            raise NotImplementedError(reason)
        db = NoSQLDatabase(cls._dbname, cls._uri)
        return db.find(cls._dbname, cls._collection, *args, **kwargs)

    @property
    def id(self):
        """Return str version of ObjectId"""
        if not self._id:
            return None
        else:
            return str(self._id)

    @id.setter
    def id(self, value):
        self._id = ObjectId(value)

    @classmethod
    def init_id(cls, id, **kwargs):
        _id = ObjectId(id)
        db = NoSQLDatabase(cls._dbname, cls._uri)
        if db.exists(cls._dbname, cls._collection, _id):
            new_object = cls(id=id, **kwargs)
        else:
            new_object = cls()
            new_object.id = id
        return new_object

    def __repr__(self):
        return str(self.to_dict())

    def __str__(self):
        return str(self.to_dict())
