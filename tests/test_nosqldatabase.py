import logging
import unittest

from irma.common.exceptions import IrmaDatabaseError, IrmaLockError
from irma.database.nosqlhandler import NoSQLDatabase
from irma.database.nosqlobjects import NoSQLDatabaseObject
from datetime import datetime
from bson import ObjectId
from irma.common.utils import IrmaLock, IrmaLockMode

# Test config
test_db_uri = "mongodb://localhost"
test_db_name = "unitest"
test_db_collection = "testobject"


# test object
class TestObject(NoSQLDatabaseObject):
    _uri = test_db_uri
    _dbname = test_db_name
    _collection = test_db_collection

    def __init__(self, dbname=None, id=None, mode=IrmaLockMode.read, save=True):
        if dbname is not None:
            self._dbname = dbname
        self.user = "test"
        self.date = datetime.now()
        self.dict = {}
        self.list = []
        super(TestObject, self).__init__(id=id, mode=mode, save=save)

    @classmethod
    def has_lock_timed_out(cls, id):
        return super(TestObject, cls).has_lock_timed_out(id)

    @classmethod
    def is_lock_free(cls, id):
        return super(TestObject, cls).is_lock_free(id)


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
        self.assertIsNotNone(t1.id)
        self.assertEquals(collection.count(), 1)

    def test_id_type_testobject(self):
        db = NoSQLDatabase(test_db_name, test_db_uri)
        dbh = db.db_instance()
        database = dbh[test_db_name]
        collection = database[test_db_collection]
        collection.remove()

        t1 = TestObject()
        self.assertEquals(type(t1._id), ObjectId)
        self.assertEquals(type(t1.id), str)

    def test_add_two_testobjects(self):
        db = NoSQLDatabase(test_db_name, test_db_uri)
        dbh = db.db_instance()
        database = dbh[test_db_name]
        collection = database[test_db_collection]
        collection.remove()

        t1 = TestObject()
        t2 = TestObject()
        self.assertNotEquals(t1.id, t2.id)
        self.assertEquals(collection.count(), 2)

    def test_check_type(self):
        db = NoSQLDatabase(test_db_name, test_db_uri)
        dbh = db.db_instance()
        database = dbh[test_db_name]
        collection = database[test_db_collection]
        collection.remove()
        t1 = TestObject()
        t2 = TestObject(id=t1.id)
        self.assertEquals(collection.count(), 1)
        self.assertEquals(type(t2.id), str)
        self.assertEquals(type(t2.list), list)
        self.assertEquals(type(t2.dict), dict)
        self.assertEquals(type(t2.user), unicode)
        self.assertEquals(type(t2.date), datetime)
        collection.remove()

    def test_check_invalid_id(self):
        with self.assertRaises(IrmaDatabaseError):
            TestObject(id="coin")

    def test_check_not_existing_id(self):
        with self.assertRaises(IrmaDatabaseError):
            TestObject(id="0")

    def test_check_insertion_with_fixed_id(self):
        t = TestObject()
        t.user = "coin"
        t.list.append(1)
        t.list.append(2)
        t.list.append(3)
        fixed_id = ObjectId()
        t.id = str(fixed_id)
        t.update()
        t2 = TestObject(id=str(fixed_id))
        self.assertEquals(t2.id, str(fixed_id))
        self.assertEquals(t2.user, "coin")
        self.assertEquals(t2.list, [1, 2, 3])

    def test_init_id(self):
        fixed_id = str(ObjectId())
        with self.assertRaises(IrmaDatabaseError):
            TestObject(id=fixed_id)
        t = TestObject.init_id(fixed_id)
        t.user = "coin"
        t.list.append(1)
        t.list.append(2)
        t.list.append(3)
        t.update()
        self.assertEquals(t.id, str(fixed_id))
        t1 = TestObject.init_id(fixed_id)
        self.assertEquals(t1.id, str(fixed_id))
        self.assertEquals(t1.user, "coin")
        self.assertEquals(t1.list, [1, 2, 3])

    def test_update(self):
        t = TestObject()
        t.user = "coin"
        t.list.append(1)
        t.list.append(2)
        t.list.append(3)
        t.update()
        self.assertEquals(t.list, [1, 2, 3])
        t.update({'user':"bla"})
        t1 = TestObject(id=t.id)
        self.assertEquals(t1.user, "bla")

class CheckLockObject(DbTestCase):
    def test_is_lock_free(self):
        t = TestObject()
        self.assertTrue(TestObject.is_lock_free(t.id))
        t.take()
        self.assertFalse(TestObject.is_lock_free(t.id))

    def test_has_lock_timed_out(self):
        t = TestObject()
        t.take()
        self.assertFalse(TestObject.has_lock_timed_out(t.id))
        t._lock_time = 0
        t.update()
        self.assertTrue(TestObject.has_lock_timed_out(t.id))

    def test_has_state_changed(self):
        t = TestObject()
        t2 = TestObject(id=t.id)
        t.date = t2.date    # the instantiation of t2 has changed the value of date in the db
        self.assertFalse(t.has_state_changed())
        t2.list.append(1)
        t2.list.append(2)
        t2.list.append(3)
        t2.update()
        self.assertTrue(t.has_state_changed())

    def test_take_release(self):
        t = TestObject()
        self.assertEquals(t._lock, IrmaLock.free)
        t.take()
        self.assertEquals(t._lock, IrmaLock.locked)
        with self.assertRaises(IrmaLockError):
            t.take()
        t.release()
        self.assertEquals(t._lock, IrmaLock.free)

if __name__ == '__main__':
    enable_logging()
    unittest.main()
