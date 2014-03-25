# Test config
import logging
import unittest
from irma.common.exceptions import IrmaDatabaseError
from irma.database.nosqlhandler import NoSQLDatabase
from irma.fileobject.handler import FileObject

test_db_uri = "mongodb://localhost"
test_db_name = "unitest"
test_db_collection = "testobject"
test_db_collection_files = "testfile"


# test object
class TestObject(FileObject):
    _uri_file = test_db_uri
    _uri = test_db_uri
    _dbname_file = test_db_name
    _dbname = test_db_name
    _collection_file = test_db_collection_files
    _collection = test_db_collection


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
            database2 = dbh[test_db_collection_files]
            collection = database[test_db_collection]
            collection2 = database2[test_db_collection_files]
            assert collection.count() <= 0
            assert collection2.count() <= 0
        except IrmaDatabaseError as e:
            print "TestDatabase Error: {0}".format(e)
            self.skipTest(DbTestCase)


class CheckFileSave(DbTestCase):
    def test_file_save_load(self):
        t = TestObject()
        data = 'Some awesome data'
        t.save(data, 'AName')
        t2 = TestObject(id=t.id)
        self.assertEqual(t2.data, data)

    def test_file_update(self):
        t = TestObject()
        t.save('Some useless data', 'AName')
        new_data = 'Some useful data'
        t.update_data(new_data)
        t2 = TestObject(id=t.id)
        self.assertEqual(t2.data, new_data)

    def test_add_altname(self):
        t = TestObject()
        data = 'Some awesome data'
        another_name = 'AnotherName'
        t.save(data, 'AName')
        t.save(data, another_name)
        t2 = TestObject(id=t.id)
        self.assertIn(another_name, t2.altnames)


if __name__ == '__main__':
    enable_logging()
    unittest.main()
