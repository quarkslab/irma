from unittest import TestCase
from mock import MagicMock

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from brain.models.sqlobjects import User
from irma.common.base.exceptions import IrmaDatabaseError, \
    IrmaDatabaseResultNotFound


class TestModelsUser(TestCase):
    def setUp(self):
        self.name = "name"
        self.rmqvhost = "rmqvhost"
        self.ftpuser = "ftpuser"
        self.session = MagicMock()

    def test001___init__(self):
        user = User(self.name, self.rmqvhost, self.ftpuser)
        self.assertEqual(user.name, self.name)
        self.assertEqual(user.rmqvhost, self.rmqvhost)
        self.assertEqual(user.ftpuser, self.ftpuser)

    def test002_get_by_rmqvhost(self):
        User.get_by_rmqvhost(self.session)
        self.session.query.assert_called_once_with(User)
        m_filter = self.session.query(User).filter
        m_filter.assert_called_once()
        m_filter().one.assert_called_once()

    def test003_get_by_rmqvhost_not_found(self):
        self.session.query.side_effect = NoResultFound
        with self.assertRaises(IrmaDatabaseResultNotFound):
            User.get_by_rmqvhost(self.session, rmqvhost="whatever")

    def test004_get_by_rmqvhost_multiple_found(self):
        self.session.query.side_effect = MultipleResultsFound
        with self.assertRaises(IrmaDatabaseError):
            User.get_by_rmqvhost(self.session, rmqvhost="whatever")
