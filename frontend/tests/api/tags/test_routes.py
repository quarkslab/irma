from unittest import TestCase

import api.tags.controllers as api_tags
from mock import MagicMock, patch

from api.tags.schemas import TagSchema


class TestTagsRoutes(TestCase):
    def assertIsTag(self, data):
        self.assertTrue(type(data) == dict)
        self.assertCountEqual(data.keys(), TagSchema().fields)

    def assertIsTagList(self, data):
        self.assertTrue(type(data) == list)
        for tag in data:
            self.assertIsTag(tag)

    def setUp(self):
        self.db = MagicMock()
        self.session = self.db.session
        self.old_db = api_tags.db
        api_tags.db = self.db

    def tearDown(self):
        api_tags.db = self.old_db
        del self.db

    @patch("api.tags.controllers.Tag")
    def test_list(self, m_Tag):
        ret = api_tags.list()
        m_Tag.query_find_all.assert_called_once_with(self.session)
        self.assertIsTagList(ret["items"])

    @patch("api.tags.controllers.Tag")
    def test_list_error(self, m_Tag):
        exception = Exception("test")
        m_Tag.query_find_all.side_effect = exception
        with self.assertRaises(Exception):
            api_tags.list()

    @patch("api.tags.controllers.Tag")
    def test_new(self, m_Tag):
        tag = "whatever"
        ret = api_tags.new(text=tag)
        m_Tag.query_find_all.assert_called_once_with(self.session)
        self.assertIsTag(ret)

    @patch("api.tags.controllers.Tag")
    def test_new_error(self, m_Tag):
        tag = "whatever"
        exception = Exception("test")
        m_Tag.query_find_all.side_effect = exception
        with self.assertRaises(Exception):
            api_tags.new(text=tag)

    @patch("api.tags.controllers.Tag")
    def test_new_error_existing(self, m_Tag):
        tag = MagicMock()
        tag.text = "whatever"
        m_Tag.query_find_all.return_value = [tag]
        with self.assertRaises(Exception):
            api_tags.new(text=tag.text)

    @patch("api.tags.controllers.Tag")
    def test_new_error_missing_text(self, m_Tag):
        with self.assertRaises(api_tags.HTTPInvalidParam):
            api_tags.new(text=None)
