import logging, unittest
from datetime import datetime, timedelta
from irma.common.exceptions import IrmaDatabaseError
from irma.database.sqlhandler import SQLDatabase
from irma.database.sqlobjects import Base, Column, Integer, String, DateTime

test_dbengine = "sqlite:///irma_test.db"

# test object
class TestObject(Base):
    __tablename__ = 'tests'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    size = Column(Integer)
    date = Column(DateTime)

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
        db = SQLDatabase(test_dbengine)
        Base.metadata.create_all(db._db)
        # check database is ready for test
        self.database_running_and_empty()

    def tearDown(self):
        with SQLDatabase(test_dbengine) as db:
            for i in db.all(TestObject):
                db.delete(i)

    def database_running_and_empty(self):
        # check that unittest database is empty before testing
        try:
            db = SQLDatabase(test_dbengine)
            assert db.count(TestObject) == 0
        except IrmaDatabaseError as e:
            print "TestDatabase Error: {0}".format(e)
            self.skipTest(DbTestCase)


class CheckAddObject(DbTestCase):

    def test_add_testobject(self):
        with SQLDatabase(test_dbengine) as db:
            test1 = TestObject(name="test1", size=10)
            db.add(test1)
            self.assertEquals(db.count(TestObject), 1)

    def test_retrieve_testobject(self):
        with SQLDatabase(test_dbengine) as db:
            test1 = TestObject(name="test1", size=10)
            db.add(test1)
        del(db)
        db = SQLDatabase(test_dbengine)
        test = db.find_by(TestObject, name="test1")
        self.assertEquals(type(test), list)
        self.assertEquals(len(test), 1)
        test1 = test[0]
        self.assertEquals(test1.name, "test1")
        self.assertEquals(test1.size, 10)

    def test_add_multiple_testobject(self):
        db = SQLDatabase(test_dbengine)
        test1 = TestObject(name="test1", size=10, date=datetime.now())
        test2 = TestObject(name="test2", size=20, date=datetime.now())
        test3 = TestObject(name="test3", size=30, date=datetime.now())
        db.add_all([test1, test2, test3])
        del(db)
        db = SQLDatabase(test_dbengine)
        self.assertEquals(db.count(TestObject), 3)

    def test_find_by_attribute(self):
        with SQLDatabase(test_dbengine) as db:
            test1 = TestObject(name="test1", size=10, date=datetime.now())
            test2 = TestObject(name="test2", size=10, date=datetime.now())
            test3 = TestObject(name="test3", size=40, date=datetime.now())
            test4 = TestObject(name="test4", size=10, date=datetime.now())
            db.add_all([test1, test2, test3, test4])
        del(db)
        db = SQLDatabase(test_dbengine)
        self.assertEquals(len(db.find_by(TestObject, size=10)), 3)
        self.assertEquals([i.name for i in db.find_by(TestObject, size=10)], ["test1", "test2", "test4"])

    def test_delete(self):
        with SQLDatabase(test_dbengine) as db:
            test1 = TestObject(name="test1", size=10, date=datetime.now())
            test2 = TestObject(name="test2", size=10, date=datetime.now())
            test3 = TestObject(name="test3", size=40, date=datetime.now())
            test4 = TestObject(name="test4", size=10, date=datetime.now())
            db.add_all([test1, test2, test3, test4])
        del(db)
        db = SQLDatabase(test_dbengine)
        self.assertEquals(db.count(TestObject), 4)
        test1 = db.find_by(TestObject, name="test1")[0]
        db.delete(test1)
        del(db)
        db = SQLDatabase(test_dbengine)
        self.assertEquals(db.count(TestObject), 3)

    def test_one(self):
        db = SQLDatabase(test_dbengine)
        test1 = TestObject(name="test1", size=10, date=datetime.now())
        test2 = TestObject(name="test2", size=10, date=datetime.now())
        test3 = TestObject(name="test3", size=30, date=datetime.now())
        db.add_all([test1, test2, test3])
        del(db)
        db = SQLDatabase(test_dbengine)
        test = db.one_by(TestObject, name="test1")
        self.assertEquals(test.size, 10)
        with self.assertRaises(IrmaDatabaseError):
            test = db.one_by(TestObject, size=10)
        with self.assertRaises(IrmaDatabaseError):
            test = db.one_by(TestObject, size=50)

    def test_time_filter(self):
        with SQLDatabase(test_dbengine) as db:
            test1 = TestObject(name="test1", size=10, date=datetime.now() - timedelta(hours=48))
            test2 = TestObject(name="test2", size=10, date=datetime.now() - timedelta(hours=24))
            test3 = TestObject(name="test3", size=40, date=datetime.now() - timedelta(hours=12))
            test4 = TestObject(name="test4", size=10, date=datetime.now())
            db.add_all([test1, test2, test3, test4])
        del(db)
        db = SQLDatabase(test_dbengine)
        self.assertEquals(len(db.find(TestObject, "date >= '{0}'".format(datetime.now() - timedelta(hours=16)))), 2)
        self.assertEquals(len(db.find(TestObject, "date >= '{0}'".format(datetime.now() - timedelta(hours=36)))), 3)
        self.assertEquals(len(db.find(TestObject, "date >= '{0}'".format(datetime.now() - timedelta(hours=72)))), 4)

    def test_and_filter(self):
        with SQLDatabase(test_dbengine) as db:
            test1 = TestObject(name="test1", size=10, date=datetime.now() - timedelta(hours=12))
            test2 = TestObject(name="test2", size=10, date=datetime.now() - timedelta(hours=12))
            test3 = TestObject(name="test3", size=40, date=datetime.now() - timedelta(hours=12))
            test4 = TestObject(name="test4", size=10, date=datetime.now())
            test5 = TestObject(name="test5", size=50, date=datetime.now())
            db.add_all([test1, test2, test3, test4, test5])
        del(db)
        db = SQLDatabase(test_dbengine)
        self.assertEquals(len(db.find(TestObject, "size == 10 and date <= '{0}'".format(datetime.now() - timedelta(hours=4)))), 2)
        self.assertEquals(len(db.find(TestObject, "name == 'test1' and date <= '{0}'".format(datetime.now() - timedelta(hours=4)))), 1)

    def test_or_filter(self):
        with SQLDatabase(test_dbengine) as db:
            test1 = TestObject(name="test1", size=10, date=datetime.now() - timedelta(hours=12))
            test2 = TestObject(name="test2", size=10, date=datetime.now() - timedelta(hours=12))
            test3 = TestObject(name="test3", size=40, date=datetime.now() - timedelta(hours=12))
            test4 = TestObject(name="test4", size=10, date=datetime.now())
            test5 = TestObject(name="test5", size=50, date=datetime.now())
            db.add_all([test1, test2, test3, test4, test5])
        del(db)
        db = SQLDatabase(test_dbengine)
        self.assertEquals(len(db.find(TestObject, "size == 10 or date <= '{0}'".format(datetime.now() - timedelta(hours=4)))), 4)

    def test_sum(self):
        with SQLDatabase(test_dbengine) as db:
            test1 = TestObject(name="test1", size=10, date=datetime.now() - timedelta(hours=12))
            test2 = TestObject(name="test2", size=20, date=datetime.now() - timedelta(hours=12))
            test3 = TestObject(name="test3", size=30, date=datetime.now() - timedelta(hours=12))
            test4 = TestObject(name="test4", size=40, date=datetime.now())
            test5 = TestObject(name="test5", size=50, date=datetime.now())
            db.add_all([test1, test2, test3, test4, test5])
        del(db)
        db = SQLDatabase(test_dbengine)
        self.assertEquals(db.sum(TestObject.size, "date >= '{0}'".format(datetime.now() - timedelta(hours=4))), 90)
        self.assertEquals(db.sum(TestObject.size, "date >= '{0}'".format(datetime.now() - timedelta(hours=20))), 150)

    def test_sum_by(self):
        with SQLDatabase(test_dbengine) as db:
            test1 = TestObject(name="test1", size=10, date=datetime.now() - timedelta(hours=12))
            test2 = TestObject(name="test1", size=20, date=datetime.now() - timedelta(hours=12))
            test3 = TestObject(name="test1", size=30, date=datetime.now() - timedelta(hours=12))
            test4 = TestObject(name="test2", size=40, date=datetime.now())
            test5 = TestObject(name="test2", size=50, date=datetime.now())
            db.add_all([test1, test2, test3, test4, test5])
        del(db)
        db = SQLDatabase(test_dbengine)
        self.assertEquals(db.sum_by(TestObject.size, name="test1"), 60)
        self.assertEquals(db.sum_by(TestObject.size, name="test2"), 90)

if __name__ == '__main__':
    enable_logging()
    unittest.main()

