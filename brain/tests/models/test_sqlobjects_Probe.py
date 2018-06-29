from unittest import TestCase
from mock import MagicMock
from random import choice

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from brain.models.sqlobjects import Probe
from irma.common.base.exceptions import IrmaDatabaseError, \
    IrmaDatabaseResultNotFound


class TestModelsProbe(TestCase):
    def setUp(self):
        self.name = "name"
        self.display_name = "display_name"
        self.category = "category"
        self.mimetype_regexp = "mimetype_regexp"
        self.online = choice([True, False])
        self.session = MagicMock()

    def test001___init__(self):
        probe = Probe(self.name, self.display_name, self.category,
                      self.mimetype_regexp, self.online)
        self.assertEqual(probe.name, self.name)
        self.assertEqual(probe.display_name, self.display_name)
        self.assertEqual(probe.category, self.category)
        self.assertEqual(probe.mimetype_regexp, self.mimetype_regexp)
        self.assertEqual(probe.online, self.online)

    def test002_get_by_name(self):
        Probe.get_by_name("whatever", self.session)
        self.session.query.assert_called_once_with(Probe)
        m_filter = self.session.query().filter
        m_filter.assert_called_once()
        m_filter().one.assert_called_once()

    def test003_get_by_name_not_found(self):
        self.session.query.side_effect = NoResultFound
        with self.assertRaises(IrmaDatabaseResultNotFound):
            Probe.get_by_name("whatever", self.session)

    def test004_get_by_name_multiple_found(self):
        self.session.query.side_effect = MultipleResultsFound
        with self.assertRaises(IrmaDatabaseError):
            Probe.get_by_name("whatever", self.session)

    def test005_all(self):
        Probe.all(self.session)
        self.session.query.assert_called_once_with(Probe)
        self.session.query().all.assert_called_once()
