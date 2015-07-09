from unittest import TestCase
from mock import patch

import frontend.api.controllers.probes as api_probes


class TestApiProbes(TestCase):

    def test001_list_ok(self):
        sample = ["test"]
        expected = {"total": len(sample),
                    "data": sample}
        with patch("frontend.api.controllers.probes.celery_brain") as mock:
            mock.probe_list.return_value = sample
            result = api_probes.list()
        self.assertEqual(api_probes.response.content_type,
                         "application/json; charset=UTF-8")
        self.assertTrue(mock.probe_list.called)
        self.assertEqual(result, expected)

    def test002_list_error(self):
        expected = Exception("test")
        celery_brain = "frontend.api.controllers.probes.celery_brain"
        with patch(celery_brain) as mock_error:
            mock_error.probe_list.side_effect = expected
            process_error = "frontend.api.controllers.probes.process_error"
            with patch(process_error) as mock:
                result = api_probes.list()
        self.assertIsNone(result)
        self.assertTrue(mock.called)
        self.assertEqual(mock.call_args, ((expected,),))
