import logging, unittest

from irma.common.exceptions import IrmaDatabaseError
from irma.database.handler import Database
from irma.database.objects import DatabaseObject
from datetime import datetime
import bson

# Test config
test_db_uri = "mongodb://localhost"
test_db_name = "unitest"
test_db_collection = "testobject"

# test object
class TestObject(DatabaseObject):
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
            db = Database(test_db_name, test_db_uri)
            dbh = db.db_instance()
            database = dbh[test_db_collection]
            collection = database[test_db_collection]
            assert collection.count() <= 10
        except Exception as e:
            print "TestDatabase Error: {0}".format(e)
            self.skipTest(DbTestCase)


class CheckSingleton(DbTestCase):

    def test_singleton(self):
        self.assertEquals(id(Database(test_db_name, test_db_uri)), id(Database(test_db_name, test_db_uri)))


class CheckAddObject(DbTestCase):


    def test_add_testobject(self):
        db = Database(test_db_name, test_db_uri)
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
        db = Database(test_db_name, test_db_uri)
        dbh = db.db_instance()
        database = dbh[test_db_name]
        collection = database[test_db_collection]
        collection.remove()

        t1 = TestObject()
        t1.save()
        self.assertEquals(type(t1._id), bson.ObjectId)
        self.assertEquals(type(t1.id), str)

    def test_add_two_testobjects(self):
        db = Database(test_db_name, test_db_uri)
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
        db = Database(test_db_name, test_db_uri)
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

"""
class CheckSetValues(unittest.TestCase):

    def test_set_scaninfo(self):
        db = Database(db_coll, dbconfig.MONGODB)
        dbh = db.db_instance()

        database = dbh[db_coll]
        collection = database[dbconfig.COLL_SCANINFO]
        collection.remove()

        s1 = ScanInfo()
        s1.probelist = ['clamav', 'kaspersky']
        s1.oids = ['1', '2', '3']
        s1.status = ScanStatus.finished
        s1.taskid = '4'
        s1.save()
        s2 = ScanInfo(_id=s1._id)
        self.assertEquals(s2.probelist, ['clamav', 'kaspersky'])
        self.assertEquals(s2.oids, ['1', '2', '3'])
        self.assertEquals(s2.status, ScanStatus.finished)
        self.assertEquals(s2.taskid, '4')

    def test_set_scanresults(self):
        db = Database(db_coll, dbconfig.MONGODB)
        dbh = db.db_instance()

        database = dbh[db_coll]
        collection = database[dbconfig.COLL_SCANRES]
        collection.remove()

        r1 = ScanResults()
        r1.clamav = { "version" : "ClamAV 0.97.8/18197/Wed Dec  4 12:41:26 2013", "result" : "Trojan.Generic.Bredolab-2" }
        r1.kaspersky = { "version" : "Kaspersky Anti-Virus (R) 14.0.0.4651", "result" : "Worm.Win32.AutoIt.r" }
        r1.save()
        r2 = ScanResults(dbname=db_coll, _id=r1._id)
        self.assertEquals(r2.clamav, { "version" : "ClamAV 0.97.8/18197/Wed Dec  4 12:41:26 2013", "result" : "Trojan.Generic.Bredolab-2" })
        self.assertEquals(r2.kaspersky, { "version" : "Kaspersky Anti-Virus (R) 14.0.0.4651", "result" : "Worm.Win32.AutoIt.r" })

class CheckDelObjects(unittest.TestCase):

    def test_del_scaninfo(self):
        db = Database(db_coll, dbconfig.MONGODB)
        dbh = db.db_instance()

        database = dbh[db_coll]
        collection = database[dbconfig.COLL_SCANINFO]
        collection.remove()

        s1 = ScanInfo(dbname=db_coll)
        self.assertIsNone(s1._id)
        s1.save()
        self.assertIsNotNone(s1._id)
        self.assertEquals(collection.count(), 1)

        s2 = ScanInfo(dbname=db_coll)
        self.assertIsNone(s2._id)
        s2.save()
        self.assertIsNotNone(s2._id)
        self.assertNotEquals(s1._id, s2._id)
        self.assertEquals(collection.count(), 2)

    def test_del_scanresults(self):
        db = Database(db_coll, dbconfig.MONGODB)
        dbh = db.db_instance()

        database = dbh[db_coll]
        collection = database[dbconfig.COLL_SCANRES]
        collection.remove()

        r1 = ScanResults(dbname=db_coll)
        r1.save()

        r2 = ScanResults(dbname=db_coll)
        r2.save()

        self.assertNotEquals(r1._id, r2._id)
        self.assertEquals(collection.count(), 2)
"""

if __name__ == '__main__':
    enable_logging()
    unittest.main()
