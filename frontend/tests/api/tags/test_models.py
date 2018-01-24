from unittest import TestCase
from mock import MagicMock

from api.tags.models import Tag


class TestTag(TestCase):

    def test___init__(self):
        text = "whatever"
        t = Tag(text=text)
        self.assertEqual(t.text, text)

    def test_to_json(self):
        text = "whatever"
        t = Tag(text=text)
        expected = {'text': text}
        self.assertEqual(t.to_json(), expected)

    def test_query_find_all(self):
        m_session = MagicMock()
        Tag.query_find_all(m_session)
        m_session.query().all.assert_called_once()
