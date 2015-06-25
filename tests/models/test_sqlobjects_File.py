from datetime import datetime
from unittest import TestCase
from mock import MagicMock, patch
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from frontend.models.sqlobjects import File
from lib.irma.database.sqlobjects import SQLDatabaseObject
from lib.irma.common.exceptions import IrmaDatabaseError
from lib.irma.common.exceptions import IrmaDatabaseResultNotFound


class TestFile(TestCase):

    def setUp(self):
        self.first_ts = 0
        self.last_ts = 1
        self.file = File(self.first_ts, self.last_ts)

    def tearDown(self):
        del self.file

    def test001___init__(self):
        self.assertEqual(self.file.timestamp_first_scan, self.first_ts)
        self.assertEqual(self.file.timestamp_last_scan, self.last_ts)
        self.assertEqual(self.file.tags, list())
        self.assertIsInstance(self.file, File)
        self.assertIsInstance(self.file, SQLDatabaseObject)

    def test002_to_json(self):
        expected = {"timestamp_first_scan": self.first_ts,
                    "timestamp_last_scan": self.last_ts}
        self.assertEqual(self.file.to_json(), expected)

    def test003_to_json_more_stuff(self):
        base = {"md5": "m_test",
                "sha1": "s_test",
                "sha256": "s256_test",
                "size": "si_test"}
        for key, value in base.items():
            setattr(self.file, key, value)
        base["timestamp_first_scan"] = self.first_ts
        base["timestamp_last_scan"] = self.last_ts
        result = self.file.to_json()
        self.assertEqual(result, base)

    def test004_classmethod_load_from_sha256_raise_NoResultFound(self):
        sample = "test"
        session = MagicMock()
        session.query.side_effect = NoResultFound(sample)
        with self.assertRaises(IrmaDatabaseResultNotFound) as context:
            File.load_from_sha256("whatever", session)
        self.assertEqual(str(context.exception), sample)

    def test005_classmethod_load_from_sha256_raise_MultipleResultNotFound(self):  # nopep8
        sample = "test"
        session = MagicMock()
        session.query.side_effect = MultipleResultsFound(sample)
        with self.assertRaises(IrmaDatabaseError) as context:
            File.load_from_sha256("whatever", session)
        self.assertEqual(str(context.exception), sample)

    def test006_classmethod_load_from_sha256_True(self):
        sample = "test"
        session = MagicMock()
        File.sha256 = sample
        result = File.load_from_sha256(sample, session)
        self.assertTrue(session.query.called)
        self.assertEqual(session.query.call_args, ((File,),))
        self.assertTrue(session.query().filter.called)
        self.assertEqual(session.query().filter.call_args, ((True,),))
        self.assertTrue(session.query().filter().one.called)
        self.assertEqual(session.query().filter().one.call_args, (tuple(),))
        self.assertEqual(result, session.query().filter().one())

    def test007_get_file_names_empty(self):
        self.assertEqual(self.file.get_file_names(), list())

    def test008_get_file_names_some(self):
        self.files_web = list(MagicMock())
