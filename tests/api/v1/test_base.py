from unittest import TestCase
from bottle import Bottle, Route
from bottle.ext.sqlalchemy import Plugin

from tests.api.v1.data import test_routes
import frontend.api.v1.base as api_base


class TestApiBase(TestCase):

    def test001_initiation(self):
        self.assertIsInstance(api_base.application, Bottle)
        self.assertIsInstance(api_base.plugin, Plugin)
        self.assertIn(api_base.plugin, api_base.application.plugins)
        for route in api_base.application.routes:
            self.assertIsInstance(route, Route)
            self.assertIn(route.rule, test_routes)
            self.assertIn(route.method, test_routes[route.rule])
