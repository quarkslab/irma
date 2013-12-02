import logging

from pymongo import Connection

from lib.irma.common.exceptions import IrmaDatabaseError
from lib.irma.common.oopatterns import Singleton

log = logging.getLogger(__name__)

class Machine(object):
    
    # TODO: Add support for both args and kwargs
    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    # See http://stackoverflow.com/questions/1305532/ to handle it in a generic way
    def to_dict(self):
        """Converts object to dict.
        @return: dict
        """
        # from http://stackoverflow.com/questions/61517/python-dictionary-from-an-objects-fields
        return dict((key, getattr(self, key)) for key in dir(self) if key not in dir(self.__class__))


# TODO: Create an abstract class so we can use multiple databases, not only mongodb
class Database(Singleton):
    """Internal database.

    This class handles the creation of the internal database and provides some
    functions for interacting with it.
    """
    
    ##########################################################################
    # Constructor and Destructor stuff
    ##########################################################################
    def __init__(self, db_uri=None):
        # TODO: Get defaults from configuration file
        self._db_name = "irma"
        self._machine_table_name = "machines"
        if not db_uri:
            self._db_uri = "mongodb://localhost"
        else:
            self._db_uri = db_uri

        self._db_conn = None
        self._db_cache = dict()
        self._tbl_cache = dict()

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

    def _table(self, db_name, tbl_name):
        database = self._database(db_name)
        # TODO: Fix collision if two tables from diffrent databases has same name
        if tbl_name not in self._tbl_cache:
            try:
                self._tbl_cache[tbl_name] = database[tbl_name]
            except Exception as e:
                raise IrmaDatabaseError("{0}".format(e))
        return self._tbl_cache[tbl_name]

    ##########################################################################
    # Public methods
    ##########################################################################

    def db_instance(self):
        return self._db_conn

    def clean_machines(self):
        machines_tbl = self._table(self._db_name, self._machine_table_name)
        try:
            machines_tbl.remove()
        except Exception as e:
            raise IrmaDatabaseError("{0}".format(e))

    def add_machine(self, label, uuid, disks, ip, os_type, os_variant, master): 
        machine = Machine(label=label, uuid=uuid, disks=disks, ip=ip, 
                          os_type=os_type, os_variant=os_variant, master=master)
        # get table descriptor and insert
        machines_tbl = self._table(self._db_name, self._machine_table_name)
        try:
            id = machines_tbl.insert(machine.to_dict())
        except Exception as e:
            raise IrmaDatabaseError("{0}".format(e))
        return id

    def del_machine(self, filter): 
        # get table descriptor and insert
        machines_tbl = self._table(self._db_name, self._machine_table_name)
        try:
            machines_tbl.remove(filter)
        except Exception as e:
            raise IrmaDatabaseError("{0}".format(e))

    def set_manager(self, spec, mm_ip, mm_type):
        # get table descriptor and update
        machines_tbl = self._table(self._db_name, self._machine_table_name)
        try:
            machines_tbl.update(spec, {"$set": {"manager_ip": mm_ip, 
                                                "manager_type": mm_type}})
        except Exception as e:
            raise IrmaDatabaseError("{0}".format(e))

