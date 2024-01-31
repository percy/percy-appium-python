# pylint: disable=[protected-access]
import unittest
from unittest.mock import Mock, patch
from percy.errors import CLIException

from percy.lib import cli_wrapper
from percy.lib.tile import Tile


class CLIWrapperTestCase(unittest.TestCase):
    def setUp(self):
        self.cli_wrapper = cli_wrapper.CLIWrapper()
        self.ignored_elements_data = {
            "ignore_elements_data": {
                "selector": "xpath: some_xpath",
                "coOrdinates": {"top": 123, "bottom": 234, "left": 234, "right": 455},
            }
        }
        self.considered_elements_data = {
            "consider_elements_data": {
                "selector": "xpath: some_xpath",
                "coOrdinates": {"top": 50, "bottom": 100, "left": 0, "right": 100},
            }
        }

    @patch.object(cli_wrapper.CLIWrapper, "_request_body", return_value={})
    def test_post_screenshot_throws_error(self, _mock_request_body):
        with patch("requests.post") as mock_requests:
            error = "some random error"
            response = Mock()
            response.json.return_value = {"error": error}
            response.status_code = 500
            response.raise_for_status.return_value = None

            mock_requests.return_value = response
            self.assertRaises(
                CLIException,
                self.cli_wrapper.post_screenshots,
                "some-name",
                {},
                [],
                "some-debug-url",
            )

    @patch.object(cli_wrapper.CLIWrapper, "_request_body", return_value={})
    def test_post_screenshot(self, _mock_request_body):
        with patch("requests.post") as mock_requests:
            response = Mock()
            response.json.return_value = {"link": "snapshot-url-link", "success": True}
            response.status_code = 200
            response.raise_for_status.return_value = None

            mock_requests.return_value = response
            post_screenshots_reponse = self.cli_wrapper.post_screenshots(
                "some-name", {}, "some-debug-url"
            )
            self.assertDictEqual(post_screenshots_reponse, response.json())

    def test_post_failed_event(self):
        with patch("requests.post") as mock_requests:
            response = Mock()
            response.json.return_value = {"link": "snapshot-url-link", "success": True}
            response.status_code = 200
            response.raise_for_status.return_value = None

            mock_requests.return_value = response
            post_failed_event_response = self.cli_wrapper.post_failed_event("some-error")
            self.assertDictEqual(post_failed_event_response, response.json())

    def test_post_screenshot_with_ignore_region_null(self):
        with patch("requests.post") as mock_requests:
            response = Mock()
            response.json.return_value = {"link": "snapshot-url-link", "success": True}
            response.status_code = 200
            response.raise_for_status.return_value = None

            mock_requests.return_value = response
            post_screenshots_reponse = self.cli_wrapper.post_screenshots(
                "some-name",
                {},
                [Tile("some-file-path", 10, 10, 20, 20)],
                "some-debug-url",
            )
            self.assertDictEqual(post_screenshots_reponse, response.json())

    def test_post_screenshot_with_ignore_region_present(self):
        with patch("requests.post") as mock_requests:
            response = Mock()
            response.json.return_value = {"link": "snapshot-url-link", "success": True}
            response.status_code = 200
            response.raise_for_status.return_value = None

            mock_requests.return_value = response
            post_screenshots_reponse = self.cli_wrapper.post_screenshots(
                "some-name",
                {},
                [Tile("some-file-path", 10, 10, 20, 20)],
                "some-debug-url",
                self.ignored_elements_data,
            )
            self.assertDictEqual(post_screenshots_reponse, response.json())

    def test_request_body(self):
        tile = Tile("some-file-path", 10, 10, 20, 20)
        tag = {"name": "Tag"}
        name = "some-name"
        debug_url = "debug-url"
        response = self.cli_wrapper._request_body(
            name, tag, [tile], debug_url, self.ignored_elements_data, self.considered_elements_data, False
        )
        self.assertEqual(response["name"], name)
        self.assertEqual(response["external_debug_url"], debug_url)
        self.assertDictEqual(response["tag"], tag)
        self.assertListEqual(response["tiles"], [dict(tile)])
        self.assertDictEqual(
            response["ignored_elements_data"], self.ignored_elements_data
        )
        self.assertDictEqual(
            response["considered_elements_data"], self.considered_elements_data
        )
        self.assertEqual(response["sync"], False)

    def test_request_body_when_optional_values_are_null(self):
        tile = Tile("some-file-path", 10, 10, 20, 20)
        tag = {"name": "Tag"}
        name = "some-name"
        debug_url = None
        ignored_elements_data = None
        considered_elements_data = None
        response = self.cli_wrapper._request_body(
            name, tag, [tile], debug_url, ignored_elements_data, considered_elements_data, True
        )
        self.assertEqual(response["name"], name)
        self.assertEqual(response["external_debug_url"], debug_url)
        self.assertDictEqual(response["tag"], tag)
        self.assertListEqual(response["tiles"], [dict(tile)])
        self.assertEqual(response["ignored_elements_data"], None)
        self.assertEqual(response["sync"], True)
