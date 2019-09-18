from unittest import TestCase
from mock import patch
import api.common.middlewares as module


class TestCommonMiddlewares(TestCase):

    def test_init(self):
        middleware = module.DatabaseSessionManager()
        self.assertIsNone(middleware.session)

    @patch("api.common.middlewares.database_session.db_session")
    def test_connect(self, m_db_session):
        middleware = module.DatabaseSessionManager()
        middleware.connect()
        self.assertEquals(middleware.session, m_db_session())

    @patch("api.common.middlewares.database_session.db_session")
    def test_close(self, m_db_session):
        middleware = module.DatabaseSessionManager()
        middleware.connect()
        m_db_session().flush.assert_not_called()
        m_db_session().close.assert_not_called()
        middleware.close()
        m_db_session().flush.assert_called_once()
        m_db_session().close.assert_called_once()
