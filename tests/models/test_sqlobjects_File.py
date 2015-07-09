from unittest import TestCase
from mock import MagicMock
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

import frontend.models.sqlobjects as module
from frontend.models.sqlobjects import File
from lib.irma.database.sqlobjects import SQLDatabaseObject
from lib.irma.common.exceptions import IrmaDatabaseError
from lib.irma.common.exceptions import IrmaDatabaseResultNotFound


class TestFile(TestCase):

    def setUp(self):
        self.first_ts = 0
        self.last_ts = 1
        self.file = File(self.first_ts, self.last_ts)
        self.old_write_sample_on_disk = module.write_sample_on_disk
        module.write_sample_on_disk = MagicMock()

    def tearDown(self):
        del self.file
        module.write_sample_on_disk = self.old_write_sample_on_disk

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
        self.assertFalse(module.write_sample_on_disk.called)

    def test005_classmethod_load_from_sha256_raise_MultipleResultNotFound(self):  # nopep8
        sample = "test"
        session = MagicMock()
        session.query.side_effect = MultipleResultsFound(sample)
        with self.assertRaises(IrmaDatabaseError) as context:
            File.load_from_sha256("whatever", session)
        self.assertEqual(str(context.exception), sample)
        self.assertFalse(module.write_sample_on_disk.called)

    def test006_classmethod_load_from_sha256_True(self):
        sha = "sha_test"
        session = MagicMock()
        session.query().filter().one().path = None
        File.sha256 = sha
        result = File.load_from_sha256(sha, session)
        self.assertTrue(session.query.called)
        self.assertEqual(session.query.call_args, ((File,),))
        self.assertTrue(session.query().filter.called)
        self.assertEqual(session.query().filter.call_args, ((True,),))
        self.assertTrue(session.query().filter().one.called)
        self.assertEqual(session.query().filter().one.call_args, (tuple(),))
        self.assertEqual(result, session.query().filter().one())
        self.assertFalse(module.write_sample_on_disk.called)

    def test007_classmethod_load_from_sha256_path_is_None(self):
        sha, data = "sha_test", "data_test"
        session = MagicMock()
        session.query().filter().one().path = None
        File.sha256 = sha
        File.data = data
        result = File.load_from_sha256(sha, session, data)
        self.assertTrue(session.query.called)
        self.assertEqual(session.query.call_args, ((File,),))
        self.assertTrue(session.query().filter.called)
        self.assertEqual(session.query().filter.call_args, ((True,),))
        self.assertTrue(session.query().filter().one.called)
        self.assertEqual(session.query().filter().one.call_args, (tuple(),))
        self.assertEqual(result, session.query().filter().one())
        self.assertTrue(module.write_sample_on_disk.called)
        self.assertEquals(module.write_sample_on_disk.call_args,
                          ((sha, data),))

    def test008_get_file_names_empty(self):
        self.assertEqual(self.file.get_file_names(), list())

    def test009_get_file_names_some(self):
        # TODO: finish this test
        self.files_web = list(MagicMock())
