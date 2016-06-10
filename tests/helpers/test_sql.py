from unittest import TestCase

import frontend.helpers.sql as module


class TestSQLHelpers(TestCase):

    def test001_generate_url_full(self):
        dbms = "dbms"
        dialect = "dialect"
        username = "username"
        passwd = "password"
        host = "host"
        dbname = "dbname"
        expected = "{}+{}://{}:{}@{}/{}".format(dbms, dialect, username,
                                                passwd, host, dbname)
        res = module.generate_url(dbms, dialect, username,
                                  passwd, host, dbname)
        self.assertEqual(res, expected)

    def test002_generate_url_no_dialect(self):
        dbms = "dbms"
        dialect = None
        username = "username"
        passwd = "password"
        host = "host"
        dbname = "dbname"
        expected = "{}://{}:{}@{}/{}".format(dbms, username,
                                             passwd, host, dbname)
        res = module.generate_url(dbms, dialect, username,
                                  passwd, host, dbname)
        self.assertEqual(res, expected)

    def test003_generate_url_no_password(self):
        dbms = "dbms"
        dialect = None
        username = "username"
        passwd = None
        host = "host"
        dbname = "dbname"
        expected = "{}://{}@{}/{}".format(dbms, username,
                                          host, dbname)
        res = module.generate_url(dbms, dialect, username,
                                  passwd, host, dbname)
        self.assertEqual(res, expected)
