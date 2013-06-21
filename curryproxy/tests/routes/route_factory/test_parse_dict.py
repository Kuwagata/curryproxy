from testtools import ExpectedException
from testtools import TestCase

from curryproxy.routes import route_factory
from curryproxy.errors import ConfigError


class TestParse_Dict(TestCase):
    def setUp(self):
        super(TestParse_Dict, self).setUp()

        self.forwarding_pattern = 'http://1.example.com/v1.0/'
        self.endpoints_pattern = 'http://1.example.com/{Endpoint_IDs}/v1.0/'
        self.endpoint_1 = {"id": "1", "url": "https://1.api.example.com/v1.0/"}
        self.endpoint_2 = {"id": "2", "url": "https://2.api.example.com/v1.0/"}
        self.endpoints = [self.endpoint_1, self.endpoint_2]

        self.forwarding_config = {'route': self.forwarding_pattern,
                                  'forwarding_url': self.endpoint_1}
        self.endpoints_config = {'route': self.endpoints_pattern,
                                 'endpoints': self.endpoints}

    def test_endpoint(self):
        config = {'route': self.endpoints_pattern,
                  'endpoints': [self.endpoint_1]}

        route = route_factory.parse_dict(config)

        self.assertTrue(self.endpoint_1['id'] in route._endpoints)
        self.assertEqual(self.endpoint_1['url'],
                         route._endpoints[self.endpoint_1['id']])

    def test_endpoints(self):
        route = route_factory.parse_dict(self.endpoints_config)

        self.assertTrue(self.endpoint_1['id'] in route._endpoints)
        self.assertEqual(self.endpoint_1['url'],
                         route._endpoints[self.endpoint_1['id']])
        self.assertTrue(self.endpoint_2['id'] in route._endpoints)
        self.assertEqual(self.endpoint_2['url'],
                         route._endpoints[self.endpoint_2['id']])

    def test_endpoints_and_forwarding_url_missing(self):
        with ExpectedException(ConfigError):
            route_factory.parse_dict({'route': self.forwarding_pattern})

    def test_endpoints_and_forwarding_url_supplied(self):
        config = {'route': self.forwarding_pattern,
                  'forwarding_url': self.endpoint_1,
                  'endpoints': self.endpoints}

        with ExpectedException(ConfigError):
            route_factory.parse_dict(config)

    def test_endpoints_priority_errors(self):
        priority_errors = [401, 404]
        route_dict = {'route': self.endpoints_pattern,
                      'endpoints': self.endpoints,
                      'priority_errors': priority_errors}

        route = route_factory.parse_dict(route_dict)

        self.assertEqual(priority_errors, route._priority_errors)

    def test_endpoints_priority_errors_missing(self):
        route = route_factory.parse_dict(self.endpoints_config)

        self.assertEqual([], route._priority_errors)

    def test_endpoints_wildcard_missing(self):
        config = {'route': self.forwarding_pattern,
                  'endpoints': self.endpoints}

        with ExpectedException(ConfigError):
            route_factory.parse_dict(config)

    def test_forwarding_url(self):
        route = route_factory.parse_dict(self.forwarding_config)

        self.assertEqual(self.endpoint_1, route._forwarding_url)

    def test_route(self):
        route = route_factory.parse_dict(self.endpoints_config)

        self.assertEqual([self.endpoints_pattern], route._url_patterns)

    def test_route_missing(self):
        with ExpectedException(ConfigError):
            route_factory.parse_dict({'endpoints': self.endpoints})