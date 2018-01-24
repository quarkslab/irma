from unittest import TestCase

from brain.models.sqlobjects import Job


class TestModelsJob(TestCase):
    def setUp(self):
        self.scan_id = "scan_id"
        self.filename = "filename"
        self.probename = "probename"

    def test___init__(self):
        job = Job(self.scan_id, self.filename, self.probename)
        self.assertEqual(job.scan_id, self.scan_id)
        self.assertEqual(job.filename, self.filename)
        self.assertEqual(job.probename, self.probename)
        self.assertIsNotNone(job.task_id)
