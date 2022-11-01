# pylint: disable=[protected-access]
import unittest
from unittest.mock import Mock, patch
from percy.errors import CLIException

from percy.lib import cli_wrapper
from percy.lib.tile import Tile


class CLIWrapperTestCase(unittest.TestCase):
    def setUp(self):
        self.cli_wrapper = cli_wrapper.CLIWrapper()

    @patch.object(cli_wrapper.CLIWrapper, '_request_body', return_value={})
    def test_post_screenshot_throws_error(self, _mock_request_body):
        with patch('requests.post') as mock_requests:
            error = 'some random error'
            response = Mock()
            response.json.return_value = {'error': error}
            response.status_code = 500
            response.raise_for_status.return_value = None

            mock_requests.return_value = response
            self.assertRaises(CLIException, self.cli_wrapper.post_screenshots, 'some-name', {}, [], 'some-debug-url')

    @patch.object(cli_wrapper.CLIWrapper, '_request_body', return_value={})
    def test_post_screenshot(self, _mock_request_body):
        with patch('requests.post') as mock_requests:
            response = Mock()
            response.json.return_value = {'link': 'snapshot-url-link', 'success': True}
            response.status_code = 200
            response.raise_for_status.return_value = None

            mock_requests.return_value = response
            post_screenshots_reponse = self.cli_wrapper.post_screenshots( 'some-name', {}, [], 'some-debug-url')
            self.assertDictEqual(post_screenshots_reponse, response.json())

    def test_request_body(self):
        tile = Tile('some-file-path', 10, 10 ,20, 20)
        tag = {'name': 'Tag'}
        name = 'some-name'
        debug_url = 'debug-url'
        response = self.cli_wrapper._request_body(name, tag, [tile], debug_url)
        self.assertEqual(response['name'], name)
        self.assertEqual(response['external_debug_url'], debug_url)
        self.assertDictEqual(response['tag'], tag)
        self.assertListEqual(response['tiles'], [dict(tile)])
