from unittest import TestCase
from mock import MagicMock, patch

import frontend.api.v1_1.controllers.tags as api_tags
from frontend.models.sqlobjects import Tag
from frontend.api.v1_1.schemas import TagSchema_v1_1
from bottle import FormsDict


class TestApiTags(TestCase):

    def setUp(self):
        self.db = MagicMock()
        self.request = MagicMock()
        self.request.query = FormsDict()
        self.old_request = api_tags.request
        api_tags.request = self.request

    def tearDown(self):
        api_tags.request = self.old_request
        del self.request

    def test001_initiation(self):
        self.assertIsInstance(api_tags.tag_schema, TagSchema_v1_1)

    @patch("frontend.api.v1_1.controllers.tags.process_error")
    @patch("frontend.api.v1_1.controllers.tags.tag_schema")
    @patch("frontend.api.v1_1.controllers.tags.Tag")
    def test002_list(self, m_Tag, m_tag_schema, m_process_error):
        api_tags.list(self.db)
        m_Tag.query_find_all.assert_called_once_with(self.db)
        m_tag_schema.dump.assert_called

    @patch("frontend.api.v1_1.controllers.tags.process_error")
    @patch("frontend.api.v1_1.controllers.tags.Tag")
    def test003_list_error(self, m_Tag, m_process_error):
        exception = Exception("test")
        m_Tag.query_find_all.side_effect = exception
        api_tags.list(self.db)
        m_process_error.assert_called_once_with(exception)

    @patch("frontend.api.v1_1.controllers.tags.process_error")
    @patch("frontend.api.v1_1.controllers.tags.tag_schema")
    @patch("frontend.api.v1_1.controllers.tags.Tag")
    def test004_new(self, m_Tag, m_tag_schema, m_process_error):
        tag = "whatever"
        self.request.json = dict()
        self.request.json['text'] = tag
        api_tags.new(self.db)
        m_Tag.query_find_all.assert_called_once_with(self.db)
        m_tag_schema.dump.assert_called

    @patch("frontend.api.v1_1.controllers.tags.process_error")
    @patch("frontend.api.v1_1.controllers.tags.Tag")
    def test005_new_error(self, m_Tag, m_process_error):
        tag = "whatever"
        self.request.json = dict()
        self.request.json['text'] = tag
        exception = Exception("test")
        m_Tag.query_find_all.side_effect = exception
        api_tags.new(self.db)
        m_process_error.assert_called_once_with(exception)

    @patch("frontend.api.v1_1.controllers.tags.process_error")
    @patch("frontend.api.v1_1.controllers.tags.Tag")
    def test006_new_error_existing(self, m_Tag, m_process_error):
        tag = MagicMock()
        tag.text = "whatever"
        self.request.json = dict()
        self.request.json['text'] = tag.text
        m_Tag.query_find_all.return_value = [tag]
        api_tags.new(self.db)
        m_process_error.assert_called()
