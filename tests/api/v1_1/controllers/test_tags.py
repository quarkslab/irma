from unittest import TestCase
from mock import MagicMock, patch

import frontend.api.v1_1.controllers.tags as api_tags
from frontend.models.sqlobjects import Tag
from frontend.api.v1_1.schemas import TagSchema_v1_1


class TestApiTags(TestCase):

    def test001_initiation(self):
        self.assertIsInstance(api_tags.tag_schema, TagSchema_v1_1)

    def test002_list_error(self):
        sample = Exception("test")
        db_mock = MagicMock()
        db_mock.query.side_effect = sample
        process_error = "frontend.api.v1_1.controllers.tags.process_error"
        with patch(process_error) as mock:
            api_tags.list(db_mock)
        self.assertTrue(db_mock.query.called)
        self.assertEqual(db_mock.query.call_args, ((Tag,),))
        self.assertTrue(mock.called)
        self.assertEqual(mock.call_args, ((sample,),))
