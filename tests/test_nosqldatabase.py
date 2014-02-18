import logging, unittest

from irma.common.exceptions import IrmaDatabaseError
from irma.database.nosqlhandler import NoSQLDatabase
from irma.database.nosqlobjects import NoSQLDatabaseObject
from datetime import datetime
import bson

# Test config
test_db_uri = "mongodb://localhost"
test_db_name = "unitest"
test_db_collection = "testobject"

# test object
class TestObject(NoSQLDatabaseObject):
    _uri = test_db_uri
    _dbname = test_db_name
    _collection = test_db_collection

    def __init__(self, _id=None):
        self.user = "test"
        self.date = datetime.now()
        self.dict = {}
        self.list = []
        super(TestObject, self).__init__(_id=_id)

##############################################################################
# Logging options
##############################################################################
def enable_logging(level=logging.INFO, handler=None, formatter=None):
    global log
    log = logging.getLogger()
    if formatter is None:
        formatter = logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s")
    if handler is None:
        handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.setLevel(level)

##############################################################################
# Test Cases
##############################################################################
class DbTestCase(unittest.TestCase):
    def setUp(self):
        # check database is ready for test
        self.database_running_and_empty()

    def tearDown(self):
        # do the teardown
        pass

    def database_running_and_empty(self):
        # check that unittest database is empty before testing
        try:
            db = NoSQLDatabase(test_db_name, test_db_uri)
            dbh = db.db_instance()
            database = dbh[test_db_collection]
            collection = database[test_db_collection]
            assert collection.count() <= 10
        except IrmaDatabaseError as e:
            print "TestDatabase Error: {0}".format(e)
            self.skipTest(DbTestCase)


class CheckSingleton(DbTestCase):

    def test_singleton(self):
        self.assertEquals(id(NoSQLDatabase(test_db_name, test_db_uri)), id(NoSQLDatabase(test_db_name, test_db_uri)))


class CheckAddObject(DbTestCase):


    def test_add_testobject(self):
        db = NoSQLDatabase(test_db_name, test_db_uri)
        dbh = db.db_instance()
        database = dbh[test_db_name]
        collection = database[test_db_collection]
        collection.remove()

        t1 = TestObject()
        self.assertIsNone(t1.id)
        t1.save()
        self.assertIsNotNone(t1.id)
        self.assertEquals(collection.count(), 1)

    def test_id_type_testobject(self):
        db = NoSQLDatabase(test_db_name, test_db_uri)
        dbh = db.db_instance()
        database = dbh[test_db_name]
        collection = database[test_db_collection]
        collection.remove()

        t1 = TestObject()
        t1.save()
        self.assertEquals(type(t1._id), bson.ObjectId)
        self.assertEquals(type(t1.id), str)

    def test_add_two_testobjects(self):
        db = NoSQLDatabase(test_db_name, test_db_uri)
        dbh = db.db_instance()
        database = dbh[test_db_name]
        collection = database[test_db_collection]
        collection.remove()

        t1 = TestObject()
        t1.save()
        t2 = TestObject()
        t2.save()
        self.assertNotEquals(t1.id, t2.id)
        self.assertEquals(collection.count(), 2)


    def test_check_type(self):
        db = NoSQLDatabase(test_db_name, test_db_uri)
        dbh = db.db_instance()
        database = dbh[test_db_name]
        collection = database[test_db_collection]
        collection.remove()
        t1 = TestObject()
        t1.save()
        t2 = TestObject(_id=t1.id)
        t2.save()
        self.assertEquals(collection.count(), 1)
        self.assertEquals(type(t2.id), str)
        self.assertEquals(type(t2.list), list)
        self.assertEquals(type(t2.dict), dict)
        self.assertEquals(type(t2.user), unicode)
        self.assertEquals(type(t2.date), datetime)
        collection.remove()

    def test_check_invalid_id(self):
        with self.assertRaises(IrmaDatabaseError):
            TestObject(_id="Jean")

    def test_check_not_existing_id(self):
        with self.assertRaises(IrmaDatabaseError):
            TestObject(_id="0")

if __name__ == '__main__':
    enable_logging()
    unittest.main()
