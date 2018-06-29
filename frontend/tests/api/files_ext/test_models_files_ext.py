import os
from unittest import TestCase
from random import randint
from mock import MagicMock, patch, call
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from api.files_ext.models import FileExt
from api.probe_results.models import ProbeResult
from irma.common.base.exceptions import IrmaDatabaseError
from irma.common.base.exceptions import IrmaDatabaseResultNotFound
from irma.common.base.utils import IrmaProbeType
import api.files_ext.models as module


class TestFileExt(TestCase):

    def setUp(self):
        self.file = MagicMock()
        self.name = "name"
        self.scan = MagicMock()
        self.fw = FileExt(self.file, self.name)

    def tearDown(self):
        del self.fw

    def test_load_from_ext_id(self):
        m_session = MagicMock()
        ext_id = "whatever"
        FileExt.load_from_ext_id(ext_id, m_session)
        m_filter = m_session.query(FileExt).filter
        m_filter.is_called_once_with(FileExt.external_id == ext_id)

    def test_load_from_ext_id_raises_noresult(self):
        m_session = MagicMock()
        ext_id = "whatever"
        m_session.query().filter().one.side_effect = NoResultFound()
        with self.assertRaises(IrmaDatabaseResultNotFound):
            FileExt.load_from_ext_id(ext_id, m_session)

    def test_load_from_ext_id_raises_multiple(self):
        m_session = MagicMock()
        ext_id = "whatever"
        m_session.query().filter().one.side_effect = MultipleResultsFound()
        with self.assertRaises(IrmaDatabaseError):
            FileExt.load_from_ext_id(ext_id, m_session)

    @patch("api.files_ext.models.File")
    @patch("api.files_ext.models.Tag")
    def test_find_by_name(self, m_Tag, m_File):
        m_session = MagicMock()
        name = "something"
        tag = MagicMock()
        tag.id = randint(0, 10)
        tags = [tag.id]
        FileExt.query_find_by_name(name, tags, m_session)
        m_session.query.called_with(m_Tag)
        m_session.query().filter_by.assert_called_once_with(id=tag.id)
        m_session.query().filter_by().one.assert_called_once()

    @patch("api.files_ext.models.File")
    @patch("api.files_ext.models.Tag")
    def test_find_by_hash(self, m_Tag, m_File):
        m_session = MagicMock()
        hash_type, hash = "something", "anotherthing"
        tag = MagicMock()
        tag.id = randint(0, 10)
        tags = [tag.id]
        FileExt.query_find_by_hash(hash_type, hash, tags, m_session)
        m_session.query.called_with(FileExt)
        m_session.query().filter_by.assert_called_once_with(id=tag.id)
        m_session.query().filter_by().one.assert_called_once()

    @patch("api.files_ext.models.File")
    @patch("api.files_ext.models.Tag")
    def test_find_by_hash_distinct_false(self, m_Tag, m_File):
        m_session = MagicMock()
        hash_type, hash = "something", "anotherthing"
        tag = MagicMock()
        tag.id = randint(0, 10)
        tags = [tag.id]
        FileExt.query_find_by_hash(hash_type, hash, tags, m_session,
                                   distinct_name=False)
        m_session.query.called_with(FileExt)
        m_session.query().filter_by.assert_called_once_with(id=tag.id)
        m_session.query().filter_by().one.assert_called_once()

    def test_probes_finished(self):
        pr1, pr2 = MagicMock(), MagicMock()
        pr1.status = None
        pr2.status = 1
        self.fw.probe_results = [pr1, pr2]
        self.assertEqual(self.fw.probes_finished, 1)

    def test_probes_finished_all_none(self):
        pr1, pr2 = MagicMock(), MagicMock()
        pr1.status = None
        pr2.status = None
        self.fw.probe_results = [pr1, pr2]
        self.assertEqual(self.fw.probes_finished, 0)

    def test_status_0(self):
        pr1, pr2 = MagicMock(), MagicMock()
        pr1.type, pr1.status = IrmaProbeType.antivirus, 0
        pr2.type, pr2.status = IrmaProbeType.antivirus, 0
        self.fw.probe_results = [pr1, pr2]
        self.assertEqual(self.fw.status, 0)

    def test_status_1(self):
        pr1, pr2 = MagicMock(), MagicMock()
        pr1.type, pr1.status = IrmaProbeType.antivirus, 0
        pr2.type, pr2.status = IrmaProbeType.antivirus, 1
        self.fw.probe_results = [pr1, pr2]
        self.assertEqual(self.fw.status, 1)

    def test_status_2(self):
        pr1, pr2 = MagicMock(), MagicMock()
        pr1.type, pr1.status = IrmaProbeType.antivirus, None
        pr2.type, pr2.status = IrmaProbeType.antivirus, 1
        self.fw.probe_results = [pr1, pr2]
        self.assertEqual(self.fw.status, None)

    def test_get_probe_results_as_list(self):
        pr1, pr2 = MagicMock(), MagicMock()
        pr1.doc = "whatever"
        pr2.doc = "something"
        self.fw.probe_results = [pr1, pr2]
        self.assertCountEqual(self.fw.get_probe_results(results_as="list"),
                              [pr1.get_details(True),
                               pr2.get_details(True)])
        pr1.get_details.assert_called_with(True)
        pr2.get_details.assert_called_with(True)

    def test_get_probe_results_as_dict(self):
        pr1, pr2 = MagicMock(), MagicMock()
        pr3 = MagicMock()
        pr1.doc = "whatever"
        pr2.doc = "something"
        pr3.status = None
        self.fw.probe_results = [pr1, pr2, pr3]
        self.assertIsInstance(self.fw.get_probe_results(results_as="dict"),
                              dict)
        pr1.get_details.assert_called_with(True)
        pr2.get_details.assert_called_with(True)
        pr3.get_details.assert_not_called()

    def test_get_probe_results_errors1(self):
        pr1, pr2 = MagicMock(), MagicMock()
        pr1.doc = "whatever"
        pr2.doc = "something"
        self.fw.probe_results = [pr1, pr2]
        with self.assertRaises(ValueError):
            self.fw.get_probe_results(results_as="unknown")

    def test_fetch_probe_results(self):
        m_pr = MagicMock()
        probename = "probe1"
        m_pr.name = probename
        self.fw.probe_results = [m_pr]
        res = self.fw.fetch_probe_result(probename)
        self.assertEqual(res, m_pr)

    def test_fetch_probe_results_none(self):
        m_pr = MagicMock()
        probename = "probe1"
        m_pr.name = probename
        self.fw.probe_results = []
        with self.assertRaises(IrmaDatabaseError):
            self.fw.fetch_probe_result(probename)

    def test_fetch_probe_results_multiple_results(self):
        m_pr = MagicMock()
        probename = "probe1"
        m_pr.name = probename
        self.fw.probe_results = [m_pr, m_pr]
        with self.assertRaises(IrmaDatabaseError):
            self.fw.fetch_probe_result(probename)

    def test_from_fobj(self):
        filename = "file"
        m_file = MagicMock()
        fw = FileExt(m_file, filename)
        self.assertIs(type(fw), FileExt)
        self.assertEqual(fw.name, "file")

    def test_set_result(self):
        m_pr = MagicMock()
        m_pr.name = "probename"
        self.fw.probe_results = [m_pr]
        probe = "probename"
        result = {'status': 1, 'type': "something"}
        self.fw.file = MagicMock()
        self.fw.set_result(probe, result)

    def test_probes_empty(self):
        self.fw.probe_results = []
        self.assertEqual(self.fw.probes, [])

    def test_probes_not_empty(self):
        m_pr1, m_pr2 = MagicMock(), MagicMock()
        probename1, probename2 = "probename1", "probename2"
        m_pr1.name = probename1
        m_pr2.name = probename2
        self.fw.probe_results = [m_pr1, m_pr2]
        self.assertCountEqual(self.fw.probes, ["probename1", "probename2"])

    @patch("api.files_ext.models.inspect")
    def test_other_results(self, m_inspect):
        m_session = MagicMock()
        ret = MagicMock()
        ret.session = m_session
        m_inspect.return_value = ret
        res = self.fw.other_results
        self.assertEqual(res,
                         m_session.query().join().filter().order_by().all())

    @patch("api.files_ext.models.log")
    def test_hook_finished_submitter_id(self, m_log):
        self.scan.date = "scan_date"
        payload = {'submitter_id': "my_kiosk_id"}
        fw = module.FileKiosk(self.file, self.name, payload)
        fw.scan = self.scan
        fw.file.sha256 = "sha256"
        fw.name = "filename"
        fw.file.timestamp_first_scan = "ts_first_scan"
        fw.file.timestamp_last_scan = "ts_last_scan"
        fw.file.size = "size"
        pr1 = MagicMock()
        fw.probe_results = [pr1]
        pr1.name = "probe1"
        pr1.type = "antivirus"
        pr1.status = "status1"
        pr1.duration = "duration1"
        pr1.results = "results1"
        pr1.get_details.return_value = pr1
        fw.hook_finished()

        expected1 = "[files_results] date: %s file_id: %s scan_id: %s "
        expected1 += "status: %s probes: %s submitter: %s submitter_id: %s"
        call1 = call(expected1,
                     'scan_date',
                     fw.external_id,
                     fw.scan.external_id, 'Clean', 'probe1',
                     'kiosk', 'my_kiosk_id')

        expected2 = '[av_results] date: %s av_name: "%s" '
        expected2 += "status: %d virus_name: \"%s\" file_id: %s "
        expected2 += "file_sha256: %s scan_id: %s duration: %f "
        expected2 += "submitter: %s submitter_id: %s"
        call2 = call(expected2,
                     'scan_date',
                     'probe1',
                     'status1',
                     'results1',
                     fw.external_id,
                     'sha256', fw.scan.external_id, 'duration1',
                     'kiosk', 'my_kiosk_id')

        m_log.info.assert_has_calls([call1])
        m_log.info.assert_has_calls([call2])

    @patch("api.files_ext.models.log")
    def test_hook_finished(self, m_log):
        self.scan.date = "scan_date"
        self.fw.scan = self.scan
        self.fw.file.sha256 = "sha256"
        self.fw.name = "filename"
        self.fw.file.timestamp_first_scan = "ts_first_scan"
        self.fw.file.timestamp_last_scan = "ts_last_scan"
        self.fw.file.size = "size"
        pr1, pr2 = MagicMock(), MagicMock()
        self.fw.probe_results = [pr1, pr2]
        pr1.name = "probe1"
        pr1.type = "antivirus"
        pr1.status = "status1"
        pr1.duration = "duration1"
        pr1.results = "results1"
        pr2.name = "probe2"
        pr2.type = "metadata"
        pr2.status = "status2"
        pr2.duration = None
        pr2.results = "results2"
        pr1.get_details.return_value = pr1
        pr2.get_details.return_value = pr2
        self.fw.hook_finished()

        expected1 = "[files_results] date: %s file_id: %s scan_id: %s "
        expected1 += "status: %s probes: %s submitter: %s submitter_id: %s"
        call1 = call(expected1,
                     'scan_date',
                     self.fw.external_id,
                     self.fw.scan.external_id, 'Clean', 'probe1, probe2',
                     'unknown', 'undefined')

        expected2 = '[av_results] date: %s av_name: "%s" '
        expected2 += "status: %d virus_name: \"%s\" file_id: %s "
        expected2 += "file_sha256: %s scan_id: %s duration: %f "
        expected2 += "submitter: %s submitter_id: %s"
        call2 = call(expected2,
                     'scan_date',
                     'probe1',
                     'status1',
                     'results1',
                     self.fw.external_id,
                     'sha256', self.fw.scan.external_id, 'duration1',
                     'unknown', 'undefined')

        expected3 = '[probe_results] date: %s name: "%s" '
        expected3 += "status: %d file_sha256: %s file_id: %s "
        expected3 += "duration: %f submitter: %s submitter_id: %s"
        call3 = call(expected3,
                     'scan_date',
                     'probe2',
                     'status2',
                     self.fw.external_id,
                     'sha256', 0, 'unknown', 'undefined')

        m_log.info.assert_has_calls([call1])
        m_log.info.assert_has_calls([call2])
        m_log.info.assert_has_calls([call3])

    def test_FileProbeResult(self):
        pr = ProbeResult("doc", "name", "status", "type")
        fe = module.FileProbeResult(self.file, self.name, pr, "depth")
        self.assertEqual(fe.probe_result_parent, pr)
        self.assertEqual(fe.depth, "depth")

    def test_FileSuricata(self):
        fe = module.FileSuricata(self.file, self.name, "context")
        self.assertEqual(fe.context, "context")
