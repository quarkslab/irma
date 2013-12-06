import logging

from pymongo import Connection

from lib.irma.common.exceptions import IrmaDatabaseError
from lib.irma.common.oopatterns import Singleton

log = logging.getLogger(__name__)

# TODO: Create an abstract class so we can use multiple databases, not only mongodb
class Database(Singleton):
    """Internal database.

    This class handles the creation of the internal database and provides some
    functions for interacting with it.
    """

    ##########################################################################
    # Constructor and Destructor stuff
    ##########################################################################
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

    def __exit__(self, type, value, traceback):
        if self._db_conn:
            self._disconnect()

    ##########################################################################
    # Private methods
    ##########################################################################

    def _connect(self):
        if self._db_conn:
            logging.warn("Already connected to database")
        try:
            self._db_conn = Connection(self._db_uri)
        except Exception as e:
            raise IrmaDatabaseError("{0}".format(e))

    def _disconnect(self):
        if not self._db_conn:
            return
        try:
            self._db_conn.disconnect()
        except Exception as e:
            raise IrmaDatabaseError("{0}".format(e))

    def _database(self, db_name):
        if not db_name in self._db_cache:
            try:
                self._db_cache[db_name] = self._db_conn[db_name]
            except Exception as e:
                raise IrmaDatabaseError("{0}".format(e))
        return self._db_cache[db_name]

    def _table(self, db_name, coll_name):
        database = self._database(db_name)
        # TODO: Fix collision if two tables from diffrent databases has same name
        if coll_name not in self._coll_cache:
            try:
                self._coll_cache[coll_name] = database[coll_name]
            except Exception as e:
                raise IrmaDatabaseError("{0}".format(e))
        return self._coll_cache[coll_name]

    ##########################################################################
    # Public methods
    ##########################################################################

    def db_instance(self):
        return self._db_conn

    def load(self, db_name, collection_name, _id):
        """ load entry _id in collection"""
        collection = self._table(db_name, collection_name)
        try:
            res = collection.find_one({'_id':_id})
        except Exception as e:
            raise IrmaDatabaseError("{0}".format(e))
        return res

    def save(self, db_name, collection_name, dict_object):
        """ save entry in collection"""
        collection = self._table(db_name, collection_name)
        try:
            _id = collection.save(dict_object)
        except Exception as e:
            raise IrmaDatabaseError("{0}".format(e))
        return _id

    def update(self, db_name, collection_name, update_dict):
        """ Update entries in collection according to the dictionnary specified"""
        collection = self._table(db_name, collection_name)
        try:
            collection.update(update_dict)
        except Exception as e:
            raise IrmaDatabaseError("{0}".format(e))

    def remove(self, db_name, collection_name, _id):
        """ Delete entrie in collection according to the dictionnary specified"""
        collection = self._table(db_name, collection_name)
        try:
            collection.remove({'_id':_id})
        except Exception as e:
            raise IrmaDatabaseError("{0}".format(e))
