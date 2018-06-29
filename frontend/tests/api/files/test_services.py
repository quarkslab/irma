from unittest import TestCase
from mock import MagicMock, patch
import api.files.services as module


class TestFileServices(TestCase):

    @patch("api.files.services.session_transaction")
    @patch("api.files.services.File")
    def test_remove_files(self, m_File, m_session_transaction):
        m_session = MagicMock()
        m_session_transaction().__enter__.return_value = m_session
        module.remove_files("whatever")
        m_File.remove_old_files.assert_called_once_with("whatever", m_session)

    @patch("api.files.services.session_transaction")
    @patch("api.files.services.File")
    def test_remove_files_size(self, m_File, m_session_transaction):
        m_session = MagicMock()
        m_session_transaction().__enter__.return_value = m_session
        module.remove_files_size("whatever")
        m_File.remove_files_max_size.assert_called_once_with("whatever",
                                                             m_session)
