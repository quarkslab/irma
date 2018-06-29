from unittest import TestCase
from mock import patch

import brain.helpers.sql as module
from irma.common.base.exceptions import IrmaDatabaseError


class TestSessions(TestCase):

    @patch("brain.helpers.sql.session")
    def test001_transaction(self, m_session):
        with module.session_transaction():
            pass
        m_session.commit.assert_called()
        m_session.rollback.assert_not_called()
        m_session.close.assert_called()

    @patch("brain.helpers.sql.session")
    def test002_transaction_error(self, m_session):
        exception = IrmaDatabaseError
        with self.assertRaises(exception):
            with module.session_transaction():
                raise exception
        m_session.commit.assert_not_called()
        m_session.rollback.assert_called()
        m_session.close.assert_called()

    @patch("brain.helpers.sql.session")
    def test003_query(self, m_session):
        with module.session_query():
            pass
        m_session.commit.assert_not_called()
        m_session.rollback.assert_not_called()
        m_session.close.assert_not_called()

    @patch("brain.helpers.sql.session")
    def test004_query_error(self, m_session):
        exception = IrmaDatabaseError
        with self.assertRaises(exception):
            with module.session_query():
                raise exception
        m_session.commit.assert_not_called()
        m_session.rollback.assert_not_called()
        m_session.close.assert_not_called()
