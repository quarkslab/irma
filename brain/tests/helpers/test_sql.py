from unittest import TestCase
from mock import patch, MagicMock

import brain.helpers.sql as module
from lib.irma.common.exceptions import IrmaDatabaseError


class TestSessions(TestCase):

    @patch("brain.helpers.sql.SQLDatabase")
    def test001_transaction(self, m_SQLDatabase):
        m_db_session = MagicMock()
        m_SQLDatabase.get_session.return_value = m_db_session
        with module.session_transaction():
            pass
        m_db_session.commit.assert_called()
        m_db_session.rollback.assert_not_called()
        m_db_session.close.assert_called()

    @patch("brain.helpers.sql.SQLDatabase")
    def test002_transaction_error(self, m_SQLDatabase):
        m_db_session = MagicMock()
        m_SQLDatabase.get_session.return_value = m_db_session
        exception = IrmaDatabaseError
        with self.assertRaises(exception):
            with module.session_transaction():
                raise exception
        m_db_session.commit.assert_not_called()
        m_db_session.rollback.assert_called()
        m_db_session.close.assert_called()

    @patch("brain.helpers.sql.SQLDatabase")
    def test003_query(self, m_SQLDatabase):
        m_db_session = MagicMock()
        m_SQLDatabase.get_session.return_value = m_db_session
        with module.session_query():
            pass
        m_db_session.commit.assert_not_called()
        m_db_session.rollback.assert_not_called()
        m_db_session.close.assert_not_called()

    @patch("brain.helpers.sql.SQLDatabase")
    def test004_query_error(self, m_SQLDatabase):
        m_db_session = MagicMock()
        m_SQLDatabase.get_session.return_value = m_db_session
        exception = IrmaDatabaseError
        with self.assertRaises(exception):
            with module.session_query():
                raise exception
        m_db_session.commit.assert_not_called()
        m_db_session.rollback.assert_not_called()
        m_db_session.close.assert_not_called()

    @patch("brain.helpers.sql.SQLDatabase")
    def test005_sql_db_connect_error(self, m_SQLDatabase):
        m_SQLDatabase.connect.side_effect = Exception()
        with self.assertRaises(IrmaDatabaseError):
            module.sql_db_connect()
