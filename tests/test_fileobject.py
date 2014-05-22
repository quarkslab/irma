#
# Copyright (c) 2014 QuarksLab.
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
import unittest
from irma.common.exceptions import IrmaDatabaseError
from irma.database.nosqlhandler import NoSQLDatabase
from irma.fileobject.handler import FileObject

# test config
test_db_uri = "mongodb://localhost"
test_db_name = "unitest"
test_db_collection = "testobject"
test_db_collection_files = "testfile"


# test object
class TestObject(FileObject):
    _uri = test_db_uri
    _dbname = test_db_name
    _collection = test_db_collection


# =================
#  Logging options
# =================
def enable_logging(level=logging.INFO, handler=None, formatter=None):
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
#  Test Cases
# ============
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
            if db.db_instance() is None:
                db._connect()
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


class TestFileObject(DbTestCase):
    def test_file_save_load(self):
        t = TestObject()
        data = 'Some awesome data'
        t.save(data, 'AName')
        t2 = TestObject(id=t.id)
        self.assertEqual(t2.data, data)

    def test_file_update_on_save(self):
        t = TestObject()
        data = 'Some awesome data'
        t.save(data, 'AName')
        self.assertEqual(t.data, data)

    def test_file_delete(self):
        t = TestObject()
        data = 'even more awesome data'
        t.save(data, 'tempfile.bin')
        t.delete()
        with self.assertRaises(IrmaDatabaseError):
            TestObject(id=t.id)

    def test_dbname(self):
        t = TestObject()
        data = 'catch me if you can'
        t.save(data, 'tempfile.bin')
        u = TestObject(dbname=TestObject._dbname, id=t.id)
        self.assertEqual(u.id, t.id)
        self.assertEqual(u.data, data)

    def test_id_none(self):
        t = TestObject()
        self.assertIsNone(t.id)

    def test_no_data(self):
        t = TestObject()
        with self.assertRaises(IrmaDatabaseError):
            t.data

if __name__ == '__main__':
    enable_logging()
    unittest.main()
