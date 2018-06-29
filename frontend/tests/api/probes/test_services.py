from unittest import TestCase

from mock import patch

import api.probes.services as module
from irma.common.base.exceptions import IrmaValueError


class TestModuleProbectrl(TestCase):

    @patch("api.probes.services.celery_brain")
    def test_check_probe(self, m_celery_brain):
        probelist = ['probe1', 'probe2']
        all_probelist = ['probe1', 'probe2', 'probe3']
        m_celery_brain.probe_list.return_value = all_probelist
        ret = module.check_probe(probelist)
        self.assertEqual(ret, probelist)

    @patch("api.probes.services.celery_brain")
    def test_check_probe_None(self, m_celery_brain):
        probelist = None
        all_probelist = ['probe1', 'probe2', 'probe3']
        m_celery_brain.probe_list.return_value = all_probelist
        ret = module.check_probe(probelist)
        self.assertEqual(ret, all_probelist)

    @patch("api.probes.services.celery_brain")
    def test_check_probe_unknown_probe(self, m_celery_brain):
        probelist = ['probe1', 'probe2', 'probe6']
        all_probelist = ['probe1', 'probe2', 'probe3']
        m_celery_brain.probe_list.return_value = all_probelist
        with self.assertRaises(IrmaValueError) as context:
            module.check_probe(probelist)
        self.assertEqual(str(context.exception), "probe probe6 unknown")
