from unittest import TestCase

import api.common.format as module
from irma.common.base.utils import IrmaProbeType
from irma.common.plugin_result import PluginResult


class TestModuleFormatters(TestCase):

    def setUp(self):
        self.result = PluginResult(name="test-name",
                                   type="test-type",
                                   version="test-version",
                                   platform="test-platform",
                                   results="test-results",
                                   database="test-database",
                                   status=0,
                                   duration=10)

    def test_unknown_formatter(self):
        result = module.IrmaFormatter.format("test-name", self.result)
        for k in ['name', 'type', 'version', 'duration', 'results',
                  'database', 'status']:
            self.assertEqual(result[k], self.result[k])
        self.assertNotIn('error', result)
        self.assertNotIn('platform', result)

    def test_error(self):
        self.result.status = -1
        self.result.error = 'Error'
        result = module.IrmaFormatter.format("test-name", self.result)
        for k in ['name', 'type', 'version', 'duration', 'status', 'error']:
            self.assertEqual(result[k], self.result[k])
        self.assertNotIn('results', result)

    def test_wrong_duration(self):
        self.result.duration = "whatever"
        result = module.IrmaFormatter.format("test-name", self.result)
        self.assertIn('error', result)
        self.assertNotIn('results', result)
        self.assertEqual(result['status'], -1)

    def test_antivirus_formatter(self):
        self.result.type = IrmaProbeType.antivirus
        result = module.IrmaFormatter.format("test-name", self.result)
        for k in ['name', 'type', 'version', 'duration', 'results']:
            self.assertEqual(result[k], self.result[k])
        self.assertTrue('database' not in result)

    def test_antivirus_formatter_error(self):
        self.result.type = IrmaProbeType.antivirus
        self.result.status = -1
        self.result.error = "test-error"
        result = module.IrmaFormatter.format("test-name", self.result)
        for k in ['name', 'type', 'version', 'duration', 'error']:
            self.assertEqual(result[k], self.result[k])
        self.assertNotIn('database', result)

    def test_vt_formatter(self):
        vt_results = {}
        vt_results['positives'] = 10
        vt_results['total'] = 20
        vt_results['permalink'] = "http://link"
        self.result.type = IrmaProbeType.external
        self.result.name = "VirusTotal"
        self.result.status = 1
        self.result.results = {}
        self.result.results = {'results': vt_results}
        result = module.IrmaFormatter.format(self.result.name, self.result)
        for k in ['name', 'type', 'version', 'duration']:
            self.assertEqual(result[k], self.result[k])
        self.assertEqual(result['results'],
                         "detected by {}/{}".format(vt_results['positives'],
                                                    vt_results['total']))
        self.assertEqual(result['external_url'],
                         vt_results['permalink'])

    def test_vt_formatter_verbose_msg(self):
        vt_results = {}
        vt_results['verbose_msg'] = "message"
        self.result.type = IrmaProbeType.external
        self.result.name = "VirusTotal"
        self.result.status = 0
        self.result.results = {}
        self.result.results = {'results': vt_results}
        result = module.IrmaFormatter.format(self.result.name, self.result)
        for k in ['name', 'type', 'version', 'duration']:
            self.assertEqual(result[k], self.result[k])
        self.assertEqual(result['results'],
                         vt_results['verbose_msg'])
        self.assertNotIn('external_url', result)

    def test_vt_formatter_error(self):
        self.result.type = IrmaProbeType.antivirus
        self.result.name = "VirusTotal"
        self.result.status = -1
        self.result.error = "test-error"
        result = module.IrmaFormatter.format("test-name", self.result)
        for k in ['name', 'type', 'version', 'duration', 'error']:
            self.assertEqual(result[k], self.result[k])
