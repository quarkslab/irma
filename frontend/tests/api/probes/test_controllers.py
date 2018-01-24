from unittest import TestCase

from mock import patch

import api.probes.controllers as api_probes


class TestApiProbes(TestCase):

    @patch("api.probes.controllers.celery_brain")
    def test_list_ok(self, m_celery_brain):
        sample = ["test"]
        expected = {"total": len(sample),
                    "data": sample}
        m_celery_brain.probe_list.return_value = sample
        result = api_probes.list()
        self.assertEqual(result, expected)

    @patch("api.probes.controllers.celery_brain")
    def test_list_error(self, m_celery_brain):
        expected = Exception("test")
        m_celery_brain.probe_list.side_effect = expected
        result = None
        with self.assertRaises(Exception):
            result = api_probes.list()
        self.assertIsNone(result)
