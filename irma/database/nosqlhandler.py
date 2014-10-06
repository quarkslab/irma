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

import logging
from time import sleep
import gridfs

from pymongo import Connection

from common.oopatterns import Singleton
from irma.common.exceptions import IrmaDatabaseError

log = logging.getLogger(__name__)


def retry_connect(func):
    """Decorator for NoSQLDatabase to retry connecting automatically
    """
    def wrapper(instance, *args, **kwargs):
        if isinstance(instance, NoSQLDatabase):
            if not instance._is_connected():
                try:
                    instance._connect()
                    return func(instance, *args, **kwargs)
                except IrmaDatabaseError as e:
                    raise e
            return func(instance, *args, **kwargs)
        else:
            raise NotImplementedError()
    return wrapper


# TODO: Create an abstract class so we can use multiple databases,
# not only mongodb
class NoSQLDatabase(Singleton):
    """Internal database.

    This class handles the creation of the internal database and provides some
    functions for interacting with it.
    """

    # ==================================
    #  Constructor and Destructor stuff
    # ==================================
    def __init__(self, db_name, db_uri):
        # TODO: Get defaults from configuration file
        self._db_name = db_name
        self._db_uri = db_uri
        self._db_conn = None
        self._db_cache = dict()
        self._coll_cache = dict()
        self._connect()

    def __del__(self):
        if self._db_conn:
            self._disconnect()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__del__()

    # =================
    #  Private methods
    # =================

    def _connect(self):
        if self._db_conn:
            log.warn("Already connected to database")
        try:
            self._db_conn = Connection(self._db_uri)
        except Exception as e:
            raise IrmaDatabaseError("{0}".format(e))

    def _disconnect(self):
        if not self._db_conn:
            return
        try:
            self._db_conn.disconnect()
            self._db_conn = None
            self._db_cache = dict()
            self._coll_cache = dict()
        except Exception as e:
            raise IrmaDatabaseError("{0}".format(e))

    def _database(self, db_name):
        if db_name not in self._db_cache:
            try:
                self._db_cache[db_name] = self._db_conn[db_name]
            except Exception as e:
                raise IrmaDatabaseError("{0}".format(e))
        return self._db_cache[db_name]

    def _table(self, db_name, coll_name):
        database = self._database(db_name)
        # TODO: Fix collision if two tables
        # from different databases have the same name
        if coll_name not in self._coll_cache:
            try:
                self._coll_cache[coll_name] = database[coll_name]
            except Exception as e:
                raise IrmaDatabaseError("{0}".format(e))
        return self._coll_cache[coll_name]

    def _is_connected(self):
        return self._db_conn is not None

    # ================
    #  Public methods
    # ================

    def db_instance(self):
        return self._db_conn

    @retry_connect
    def load(self, db_name, collection_name, _id):
        """ load entry _id in collection"""
        collection = self._table(db_name, collection_name)
        try:
            res = collection.find_one({'_id': _id})
            return res
        except Exception as e:
            raise IrmaDatabaseError("{0}".format(e))

    @retry_connect
    def exists(self, db_name, collection_name, _id):
        """ check if entry with _id is in collection"""
        collection = self._table(db_name, collection_name)
        try:
            res = collection.find_one({'_id': _id})
            return res is not None
        except Exception as e:
            raise IrmaDatabaseError("{0}".format(e))

    @retry_connect
    def save(self, db_name, collection_name, dict_object):
        """ save entry in collection"""
        collection = self._table(db_name, collection_name)
        try:
            _id = collection.save(dict_object)
            return _id
        except Exception as e:
            raise IrmaDatabaseError("{0}".format(e))

    @retry_connect
    def update(self, db_name, collection_name, _id, update_dict):
        """
        Update entries in collection according to
        the dictionnary specified
        """
        collection = self._table(db_name, collection_name)
        try:
            collection.update({"_id": _id}, {"$set": update_dict})
        except Exception as e:
            raise IrmaDatabaseError("{0}".format(e))

    @retry_connect
    def remove(self, db_name, collection_name, _id):
        """ Delete entry in collection according to the given id"""
        collection = self._table(db_name, collection_name)
        try:
            collection.remove({'_id': _id})
        except Exception as e:
            raise IrmaDatabaseError("{0}".format(e))

    @retry_connect
    def find(self, db_name, collection_name, *args, **kwargs):
        """ Returns elements from the collection according to the given query

        :param db_name: The database
        :param collection_name: The name of the collection
        :param *args **kwargs: see
            http://api.mongodb.org/python/current/api/pymongo/collection.html#\
            pymongo.collection.Collection.find
            and http://docs.mongodb.org/manual/tutorial/query-documents/
        :rtype: cursor, see http://api.mongodb.org/python/current/api/pymongo/\
        cursor.html#pymongo.cursor.Cursor
                and http://docs.mongodb.org/manual/core/cursors/
        :return: the result of the query
        """
        collection = self._table(db_name, collection_name)
        try:
            return collection.find(*args, **kwargs)
        except Exception as e:
            raise IrmaDatabaseError("{0}".format(e))

    @retry_connect
    def put_file(self, db_name, collection_name, data, name):
        """ put data into gridfs """
        fsdbh = gridfs.GridFS(self._database(db_name),
                              collection=collection_name)
        # create a new record
        try:
            file_oid = fsdbh.put(data, filename=name)
            return file_oid
        except Exception as e:
            raise IrmaDatabaseError("{0}".format(e))

    @retry_connect
    def get_file(self, db_name, collection_name, file_oid):
        """ get data from gridfs by file object-id """
        fsdbh = gridfs.GridFS(self._database(db_name),
                              collection=collection_name)
        try:
            return fsdbh.get(file_oid)
        except Exception as e:
            raise IrmaDatabaseError("{0}".format(e))

    @retry_connect
    def delete_file(self, db_name, collection_name, file_oid):
        """ delete from gridfs by file object-id """
        fsdbh = gridfs.GridFS(self._database(db_name),
                              collection=collection_name)
        try:
            return fsdbh.delete(file_oid)
        except Exception as e:
            raise IrmaDatabaseError("{0}".format(e))
