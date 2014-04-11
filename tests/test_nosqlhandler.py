import logging
import unittest
from irma.database.nosqlhandler import NoSQLDatabase
from pymongo import Connection

# Test config
test_db_uri = "mongodb://localhost"
test_db_name = "unitest"
test_db_collection = "testobject"


# =================
#  Logging options
# =================

def enable_logging(level=logging.INFO,
                   handler=None,
                   formatter=None):
    global log
    log = logging.getLogger()
    if formatter is None:
        formatter = logging.Formatter("%(asctime)s [%(name)s] " +
                                      "%(levelname)s: %(message)s")
    if handler is None:
        handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.setLevel(level)


# ============
#  Test cases
# ============

class NoSQLDatabaseTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        enable_logging()

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass


class CheckNoSQLDatabase(NoSQLDatabaseTestCase):
    def test_init_connection_disconnection(self):
        db = NoSQLDatabase(test_db_name, test_db_uri)
        self.assertIsInstance(db.db_instance(), Connection)
        self.assertIsNotNone(db.db_instance().host)
        db._connect()
        db._disconnect()
        self.assertIsNone(db.db_instance())
        db._disconnect()
        db._db_conn = None
        db._disconnect()

    def test_del(self):
        db = NoSQLDatabase(test_db_name, test_db_uri)
        del db

    def test_with(self):
        with NoSQLDatabase(test_db_name, test_db_uri) as db:
            db._disconnect()

if __name__ == '__main__':
    unittest.main()
