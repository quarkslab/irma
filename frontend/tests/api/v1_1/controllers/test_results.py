from unittest import TestCase
from mock import MagicMock, patch

import frontend.api.v1_1.controllers.results as api_results
from frontend.models.sqlobjects import FileWeb


class TestResultsFiles(TestCase):
    @patch("frontend.api.v1_1.controllers.results.FileWeb")
    @patch("frontend.api.v1_1.controllers.results.FileWebSchema_v1_1")
    @patch("frontend.api.v1_1.controllers.results.validate_id")
    def test001_get_ok(self, m_validate_id, m_fw_schema,
                       m_FileWeb):
        db_mock = MagicMock()
        expected = m_fw_schema().dumps().data
        resultid = "whatever"
        result = api_results.get(resultid, db_mock)
        m_validate_id.assert_called_once_with(resultid)
        m_FileWeb.load_from_ext_id.assert_called_once_with(resultid, db_mock)
        self.assertEqual(result, expected)
        self.assertEqual(api_results.response.content_type,
                         "application/json; charset=UTF-8")

    @patch("frontend.api.v1_1.controllers.results.request")
    @patch("frontend.api.v1_1.controllers.results.FileWeb")
    @patch("frontend.api.v1_1.controllers.results.validate_id")
    def test002_get_formatted_ok(self, m_validate_id, m_FileWeb,
                                 m_request):
        db_mock = MagicMock()
        resultid = "whatever"
        m_request.formatted = True
        m_FileWeb.load_from_ext_id.return_value = FileWeb(None, None,
                                                          None, None)
        api_results.get(resultid, db_mock)
        m_validate_id.assert_called_once_with(resultid)
        m_FileWeb.load_from_ext_id.assert_called_once_with(resultid, db_mock)
        self.assertEqual(api_results.response.content_type,
                         "application/json; charset=UTF-8")

    @patch("frontend.api.v1_1.controllers.results.process_error")
    @patch("frontend.api.v1_1.controllers.results.validate_id")
    def test003_get_error(self, m_validate_id, m_process_error):
        db_mock = MagicMock()
        exception = Exception("test")
        m_validate_id.side_effect = exception
        resultid = "whatever"
        api_results.get(resultid, db_mock)
        m_process_error.assert_called_once_with(exception)
