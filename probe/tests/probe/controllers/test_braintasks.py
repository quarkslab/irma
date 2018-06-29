from unittest import TestCase
from mock import patch
import probe.controllers.braintasks as module


class TestBrainTasks(TestCase):

    @patch("probe.controllers.braintasks.async_call")
    def test_register_probe(self, m_async_call):
        module.register_probe("name", "displayname", "category",
                              "mimetype_regexp")
        m_async_call.assert_called_with(module.brain_app,
                                        'brain.scan_tasks',
                                        'register_probe',
                                        args=['name',
                                              'displayname',
                                              'category',
                                              'mimetype_regexp'])
