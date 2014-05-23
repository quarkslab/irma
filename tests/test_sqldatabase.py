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
import os
from datetime import datetime, timedelta
from irma.common.exceptions import IrmaDatabaseError
from irma.database.sqlhandler import SQLDatabase
from irma.database.sqlobjects import Base, Column, Integer, String, DateTime

cwd = os.path.abspath(__file__)
test_dbfile = "irma_test.db"
test_dbengine = "sqlite:///" + test_dbfile


# =============
#  Test object
# =============
class TestObject(Base):
    __tablename__ = 'tests'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    size = Column(Integer)
    date = Column(DateTime)


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
        self.db = SQLDatabase(test_dbengine)
        Base.metadata.create_all(self.db._db)
        # check database is ready for test
        self.database_running_and_empty()

    def tearDown(self):
        del self.db
        os.remove(test_dbfile)

    def database_running_and_empty(self):
        # check that unittest database is empty before testing
        try:
            assert self.db.count(TestObject) == 0
        except Exception as e:
            print "TestDatabase Error: {0}".format(e)
            self.skipTest(DbTestCase)


class TestSqlObject(DbTestCase):

    def test_add_testobject(self):
        test1 = TestObject(name="test1", size=10)
        self.db.add(test1)

        self.assertEqual(self.db.count(TestObject), 1)

    def test_retrieve_testobject(self):
        test1 = TestObject(name="test1", size=10)
        self.db.add(test1)

        test = self.db.find_by(TestObject, name="test1")
        self.assertEqual(type(test), list)
        self.assertEqual(len(test), 1)
        test1 = test[0]
        self.assertEqual(test1.name, "test1")
        self.assertEqual(test1.size, 10)

    def test_add_multiple_testobject(self):
        test1 = TestObject(name="test1", size=10, date=datetime.now())
        test2 = TestObject(name="test2", size=20, date=datetime.now())
        test3 = TestObject(name="test3", size=30, date=datetime.now())
        self.db.add_all([test1, test2, test3])

        self.assertEqual(self.db.count(TestObject), 3)

    def test_find_by_attribute(self):
        test1 = TestObject(name="test1", size=10, date=datetime.now())
        test2 = TestObject(name="test2", size=10, date=datetime.now())
        test3 = TestObject(name="test3", size=40, date=datetime.now())
        test4 = TestObject(name="test4", size=10, date=datetime.now())
        self.db.add_all([test1, test2, test3, test4])

        self.assertEqual(len(self.db.find_by(TestObject, size=10)), 3)
        self.assertEqual(
            [i.name for i in self.db.find_by(TestObject, size=10)],
            ["test1", "test2", "test4"]
        )

    def test_delete(self):
        test1 = TestObject(name="test1", size=10, date=datetime.now())
        test2 = TestObject(name="test2", size=10, date=datetime.now())
        test3 = TestObject(name="test3", size=40, date=datetime.now())
        test4 = TestObject(name="test4", size=10, date=datetime.now())
        self.db.add_all([test1, test2, test3, test4])

        self.assertEqual(self.db.count(TestObject), 4)
        test1 = self.db.find_by(TestObject, name="test1")[0]
        self.db.delete(test1)
        self.assertEqual(self.db.count(TestObject), 3)

    def test_all(self):
        test1 = TestObject(name="test1", size=10, date=datetime.now())
        test2 = TestObject(name="test2", size=10, date=datetime.now())
        test3 = TestObject(name="test3", size=30, date=datetime.now())
        self.db.add_all([test1, test2, test3])

        test = self.db.all(TestObject)
        self.assertEqual(len(test), 3)

    def test_one_by(self):
        test1 = TestObject(name="test1", size=10, date=datetime.now())
        test2 = TestObject(name="test2", size=10, date=datetime.now())
        test3 = TestObject(name="test3", size=30, date=datetime.now())
        self.db.add_all([test1, test2, test3])

        test = self.db.one_by(TestObject, name="test1")
        self.assertEqual(test.size, 10)
        with self.assertRaises(IrmaDatabaseError):
            test = self.db.one_by(TestObject, size=10)
        with self.assertRaises(IrmaDatabaseError):
            test = self.db.one_by(TestObject, size=50)

    def test_time_filter(self):
        test1 = TestObject(name="test1", size=10,
                           date=datetime.now() - timedelta(hours=48))
        test2 = TestObject(name="test2", size=10,
                           date=datetime.now() - timedelta(hours=24))
        test3 = TestObject(name="test3", size=40,
                           date=datetime.now() - timedelta(hours=12))
        test4 = TestObject(name="test4", size=10,
                           date=datetime.now())
        self.db.add_all([test1, test2, test3, test4])

        date_param = datetime.now() - timedelta(hours=16)
        find_param = "date >= '{0}'".format(date_param)
        self.assertEqual(len(self.db.find(TestObject, find_param)), 2)
        date_param = datetime.now() - timedelta(hours=36)
        find_param = "date >= '{0}'".format(date_param)
        self.assertEqual(len(self.db.find(TestObject, find_param)), 3)
        date_param = datetime.now() - timedelta(hours=72)
        find_param = "date >= '{0}'".format(date_param)
        self.assertEqual(len(self.db.find(TestObject, find_param)), 4)

    def test_and_filter(self):
        test1 = TestObject(name="test1",
                           size=10,
                           date=datetime.now() - timedelta(hours=12))
        test2 = TestObject(name="test2",
                           size=10,
                           date=datetime.now() - timedelta(hours=12))
        test3 = TestObject(name="test3",
                           size=40,
                           date=datetime.now() - timedelta(hours=12))
        test4 = TestObject(name="test4",
                           size=10,
                           date=datetime.now())
        test5 = TestObject(name="test5",
                           size=50,
                           date=datetime.now())
        self.db.add_all([test1, test2, test3, test4, test5])

        date_param = datetime.now() - timedelta(hours=4)
        find_param = "size == 10 and date <= '{0}'".format(date_param)
        self.assertEqual(len(self.db.find(TestObject, find_param)), 2)
        date_param = datetime.now() - timedelta(hours=4)
        find_param = "name == 'test1' and date <= '{0}'".format(date_param)
        self.assertEqual(len(self.db.find(TestObject, find_param)), 1)

    def test_or_filter(self):
        test1 = TestObject(name="test1",
                           size=10,
                           date=datetime.now() - timedelta(hours=12))
        test2 = TestObject(name="test2",
                           size=10,
                           date=datetime.now() - timedelta(hours=12))
        test3 = TestObject(name="test3",
                           size=40,
                           date=datetime.now() - timedelta(hours=12))
        test4 = TestObject(name="test4",
                           size=10,
                           date=datetime.now())
        test5 = TestObject(name="test5",
                           size=50,
                           date=datetime.now())
        self.db.add_all([test1, test2, test3, test4, test5])

        date_param = datetime.now() - timedelta(hours=4)
        find_param = "size == 10 or date <= '{0}'".format(date_param)
        self.assertEqual(len(self.db.find(TestObject, find_param)), 4)

    def test_sum(self):
        test1 = TestObject(name="test1",
                           size=10,
                           date=datetime.now() - timedelta(hours=12))
        test2 = TestObject(name="test2",
                           size=20,
                           date=datetime.now() - timedelta(hours=12))
        test3 = TestObject(name="test3",
                           size=30,
                           date=datetime.now() - timedelta(hours=12))
        test4 = TestObject(name="test4",
                           size=40,
                           date=datetime.now())
        test5 = TestObject(name="test5",
                           size=50,
                           date=datetime.now())
        self.db.add_all([test1, test2, test3, test4, test5])

        date_param = datetime.now() - timedelta(hours=4)
        find_param = "date >= '{0}'".format(date_param)
        self.assertEqual(self.db.sum(TestObject.size, find_param), 90)
        date_param = datetime.now() - timedelta(hours=20)
        find_param = "date >= '{0}'".format(date_param)
        self.assertEqual(self.db.sum(TestObject.size, find_param), 150)

    def test_sum_by(self):
        test1 = TestObject(name="test1",
                           size=10,
                           date=datetime.now() - timedelta(hours=12))
        test2 = TestObject(name="test1",
                           size=20,
                           date=datetime.now() - timedelta(hours=12))
        test3 = TestObject(name="test1",
                           size=30,
                           date=datetime.now() - timedelta(hours=12))
        test4 = TestObject(name="test2",
                           size=40,
                           date=datetime.now())
        test5 = TestObject(name="test2",
                           size=50,
                           date=datetime.now())
        self.db.add_all([test1, test2, test3, test4, test5])

        self.assertEqual(self.db.sum_by(TestObject.size, name="test1"), 60)
        self.assertEqual(self.db.sum_by(TestObject.size, name="test2"), 90)

    def test_one(self):
        test1 = TestObject(name="test1", size=10, date=datetime.now())
        self.db.add(test1)
        self.db.commit()

        test2 = self.db.one(TestObject, 'name = "test1"')
        self.assertEqual(test1.size, test2.size)

    def test_one_no_result(self):
        with self.assertRaises(IrmaDatabaseError):
            self.db.one(TestObject, 'name = "test1"')

    def test_one_multiple_result(self):
        test1 = TestObject(name="test1", size=10, date=datetime.now())
        test2 = TestObject(name="test1", size=20, date=datetime.now())
        self.db.add_all([test1, test2])
        self.db.commit()

        with self.assertRaises(IrmaDatabaseError):
            self.db.one(TestObject, 'name = "test1"')

    def test_rollback(self):
        test1 = TestObject(name="test1", size=10, date=datetime.now())
        self.db.add(test1)
        self.db.rollback()
        with self.assertRaises(IrmaDatabaseError):
            self.db.one(TestObject, 'name = "test1"')

    def test_disconnect(self):
        # should not raise
        # coverage tests
        self.db._disconnect()
        self.db._disconnect()

if __name__ == '__main__':
    enable_logging()
    unittest.main()
