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
import unittest
from irma.common.exceptions import IrmaDatabaseError, IrmaValueError
from irma.database.nosqlhandler import NoSQLDatabase
from irma.database.nosqlobjects import NoSQLDatabaseObject
from datetime import datetime
from bson import ObjectId

# Test config
test_db_uri = "mongodb://localhost"
test_db_name = "unitest"
test_db_collection = "testobject"


# test object
class TestObject(NoSQLDatabaseObject):
    _uri = test_db_uri
    _dbname = test_db_name
    _collection = test_db_collection

    def __init__(self,
                 dbname=None,
                 id=None,
                 save=True):
        if dbname is not None:
            self._dbname = dbname
        self.user = "test"
        self.date = datetime.now()
        self.dict = {}
        self.list = []
        super(TestObject, self).__init__(id=id, save=save)

    @classmethod
    def has_lock_timed_out(cls, id):
        return super(TestObject, cls).has_lock_timed_out(id)

    @classmethod
    def is_lock_free(cls, id):
        return super(TestObject, cls).is_lock_free(id)


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

class DbTestCase(unittest.TestCase):
    def setUp(self):
        self.db = NoSQLDatabase(test_db_name, test_db_uri)
        if self.db.db_instance() is None:
            self.db._connect()
        dbh = self.db.db_instance()
        database = dbh[test_db_name]
        self.collection = database[test_db_collection]
        self.collection.remove()

    def tearDown(self):
        self.db._disconnect()


class CheckSingleton(DbTestCase):
    def test_singleton(self):
        self.assertEqual(id(NoSQLDatabase(test_db_name, test_db_uri)),
                         id(NoSQLDatabase(test_db_name, test_db_uri)))


class TestNoSQLDatabaseObject(DbTestCase):
    def test_virtualconstructor(self):
        with self.assertRaises(IrmaValueError):
            NoSQLDatabaseObject()

    def test_add_testobject(self):
        t1 = TestObject()
        self.assertIsNotNone(t1.id)
        self.assertEqual(self.collection.count(), 1)

    def test_id_type_testobject(self):
        t1 = TestObject()
        self.assertEqual(type(t1._id), ObjectId)
        self.assertEqual(type(t1.id), str)

    def test_add_two_testobjects(self):
        t1 = TestObject()
        t2 = TestObject()
        self.assertNotEquals(t1.id, t2.id)
        self.assertEqual(self.collection.count(), 2)

    def test_check_type(self):
        t1 = TestObject()
        t2 = TestObject(id=t1.id)
        self.assertEqual(self.collection.count(), 1)
        self.assertEqual(type(t2.id), str)
        self.assertEqual(type(t2.list), list)
        self.assertEqual(type(t2.dict), dict)
        self.assertEqual(type(t2.user), unicode)
        self.assertEqual(type(t2.date), datetime)

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
        self.assertEqual(t2.id, str(fixed_id))
        self.assertEqual(t2.user, "coin")
        self.assertEqual(t2.list, [1, 2, 3])

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
        self.assertEqual(t.id, str(fixed_id))
        t1 = TestObject.init_id(fixed_id)
        self.assertEqual(t1.id, str(fixed_id))
        self.assertEqual(t1.user, "coin")
        self.assertEqual(t1.list, [1, 2, 3])

    def test_update(self):
        t = TestObject()
        t.user = "coin"
        t.list.append(1)
        t.list.append(2)
        t.list.append(3)
        t.update()
        self.assertEqual(t.list, [1, 2, 3])
        t.update({'user': "bla"})
        t1 = TestObject(id=t.id)
        self.assertEqual(t1.user, "bla")

    def test_remove(self):
        t1 = TestObject()
        self.assertEqual(self.collection.count(), 1)
        t1.remove()
        self.assertEqual(self.collection.count(), 0)

    def test_get_temp_instance(self):
        with self.assertRaises(NotImplementedError):
            NoSQLDatabaseObject.get_temp_instance(0)

        t1 = TestObject()
        temp_id = t1.id
        self.assertIsNotNone(TestObject.get_temp_instance(temp_id))
        t1.remove()
        with self.assertRaises(IrmaDatabaseError):
            TestObject.get_temp_instance(temp_id)

    def test_find(self):
        with self.assertRaises(NotImplementedError):
            NoSQLDatabaseObject.find()

        self.assertEqual(TestObject.find().count(), 0)
        t1 = TestObject()
        self.assertEqual(TestObject.find().count(), 1)

    def test_instance_to_str(self):
        t1 = TestObject()
        self.assertIsInstance(t1.__repr__(), str)
        self.assertIsInstance(t1.__str__(), str)


if __name__ == '__main__':
    enable_logging()
    unittest.main()
