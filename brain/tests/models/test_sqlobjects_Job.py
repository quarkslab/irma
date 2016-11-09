from unittest import TestCase

from brain.models.sqlobjects import Job


class TestModelsJob(TestCase):
    def setUp(self):
        self.scan_id = "scanid"
        self.filehash = "filehash"
        self.probename = "probename"

    def test001___init__(self):
        job = Job(self.scan_id, self.filehash, self.probename)
        self.assertEqual(job.scan_id, self.scan_id)
        self.assertEqual(job.filehash, self.filehash)
        self.assertEqual(job.probename, self.probename)
        self.assertIsNotNone(job.task_id)
