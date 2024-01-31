# pylint: disable=[arguments-differ]
import unittest
import json
from unittest.mock import patch, MagicMock, PropertyMock, Mock
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from appium.webdriver.webdriver import WebDriver
from appium.webdriver.common.appiumby import AppiumBy


import httpretty

from percy import percy_screenshot
from percy.common import LABEL
from percy.lib.cli_wrapper import CLIWrapper
from percy.metadata import Metadata
from percy.lib.app_percy import AppPercy
from percy.providers.generic_provider import GenericProvider
from tests.mocks.mock_methods import android_capabilities


# mock a simple webpage to screenshot
class MockServerRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write("Screenshot Me".encode("utf-8"))


# daemon threads automatically shut down when the main process exits
mock_server = HTTPServer(("localhost", 8000), MockServerRequestHandler)
mock_server_thread = Thread(target=mock_server.serve_forever)
mock_server_thread.daemon = True
mock_server_thread.start()


# mock helpers
def mock_healthcheck(fail=False, fail_how="error", type="AppPercy"):
    health_body = json.dumps({ "success": True, "build": {"id": "123", "url": "dummy_url"}, "type": type })
    health_headers = {"X-Percy-Core-Version": "1.27.0-beta.1"}
    health_status = 200

    if fail and fail_how == "error":
        health_body = '{ "success": false, "error": "test" }'
        health_status = 500
    elif fail and fail_how == "wrong-version":
        health_headers = {"X-Percy-Core-Version": "2.0.0"}
    elif fail and fail_how == "no-version":
        health_headers = {}

    httpretty.register_uri(
        httpretty.GET,
        "http://localhost:5338/percy/healthcheck",
        body=health_body,
        adding_headers=health_headers,
        status=health_status,
    )


def mock_screenshot(fail=False):
    httpretty.register_uri(
        httpretty.POST,
        "http://localhost:5338/percy/comparison",
        body=(
            '{ "success": ' + ("true" if not fail else 'false, "error": "test"') + "}"
        ),
        status=(500 if fail else 200),
    )

def mock_poa_screenshot(fail=False, sync=False):
    body = '{ "success": ' + ("true" if not fail else 'false, "error": "test"') + "}"
    if sync: body = '{ "success": "true", "data": "sync-data" }'
    httpretty.register_uri(
        httpretty.POST,
        "http://localhost:5338/percy/automateScreenshot",
        body=body,
        status=(500 if fail else 200),
    )


class TestPercyScreenshot(unittest.TestCase):
    @patch("appium.webdriver.webdriver.WebDriver")
    def setUp(self, mock_webdriver) -> None:
        mock_webdriver.__class__ = WebDriver
        CLIWrapper.is_percy_enabled.cache_clear()
        httpretty.enable()
        self.maxDiff = None
        self.mock_webdriver = mock_webdriver
        self.mock_webdriver.capabilities = android_capabilities
        self.mock_webdriver.orientation = "PORTRAIT"
        self.mock_webdriver.get_system_bars.return_value = {
            "statusBar": {"height": 10, "width": 20},
            "navigationBar": {"height": 10, "width": 20},
        }

    def tearDown(self):
        httpretty.disable()
        httpretty.reset()

    @patch.object(
        GenericProvider, "_write_screenshot", MagicMock(return_value="path-to-png-file")
    )
    @patch("appium.webdriver.webdriver.WebDriver")
    def test_throws_error_when_app_percy_arg_type_mismatch(self, mock_webdriver):
        mock_ios_webdriver = mock_webdriver
        mock_ios_webdriver.capabilities = android_capabilities
        with patch(
            "percy.metadata.IOSMetadata.remote_url", new_callable=PropertyMock
        ) as mock_remote_url:
            mock_remote_url.return_value = ""
            app_percy = AppPercy(self.mock_webdriver)
            self.assertRaises(TypeError, app_percy.screenshot, 123)
            self.assertRaises(
                TypeError, app_percy.screenshot, "screenshot 1", device_name=123
            )
            self.assertRaises(
                TypeError, app_percy.screenshot, "screenshot 1", full_screen=123
            )
            self.assertRaises(
                TypeError, app_percy.screenshot, "screenshot 1", orientation=123
            )
            self.assertRaises(
                TypeError,
                app_percy.screenshot,
                "screenshot 1",
                status_bar_height="height",
            )
            self.assertRaises(
                TypeError, app_percy.screenshot, "screenshot 1", nav_bar_height="height"
            )

    def test_throws_error_when_a_driver_is_not_provided(self):
        with self.assertRaises(Exception):
            percy_screenshot()

    #
    def test_throws_error_when_a_name_is_not_provided(self):
        with self.assertRaises(Exception):
            percy_screenshot(self.mock_webdriver)

    def test_disables_screenshots_when_the_healthcheck_fails(self):
        mock_healthcheck(fail=True)

        with patch("builtins.print") as mock_print:
            percy_screenshot(self.mock_webdriver, "screenshot 1")
            percy_screenshot(self.mock_webdriver, "screenshot 2")

            mock_print.assert_called_with(
                f"{LABEL} Percy is not running, disabling screenshots"
            )

        self.assertEqual(httpretty.last_request().path, "/percy/healthcheck")

    def test_disables_screenshots_when_the_healthcheck_version_is_wrong(self):
        mock_healthcheck(fail=True, fail_how="wrong-version")

        with patch("builtins.print") as mock_print:
            percy_screenshot(self.mock_webdriver, "screenshot 1")
            percy_screenshot(self.mock_webdriver, "screenshot 2")

            mock_print.assert_called_with(
                f"{LABEL} Unsupported Percy CLI version, 2.0.0"
            )

        self.assertEqual(httpretty.last_request().path, "/percy/healthcheck")

    @patch.object(
        Metadata, "session_id", PropertyMock(return_value="unique_session_id")
    )
    @patch.object(
        GenericProvider, "_write_screenshot", MagicMock(return_value="path-to-png-file")
    )
    def test_posts_multiple_screenshots_to_the_local_percy_server(self):
        mock_healthcheck()
        mock_screenshot()

        percy_screenshot(self.mock_webdriver, "screenshot 1")
        percy_screenshot(self.mock_webdriver, "screenshot 2", full_screen=False)

        self.assertEqual(httpretty.last_request().path, "/percy/comparison")

        body = httpretty.latest_requests()[2].parsed_body

        # self.assertEqual(s1['name'], 'screenshot 1')
        self.assertRegex(body["client_info"], r"percy-appium-app/\d+")
        self.assertRegex(body["environment_info"][0], r"appium/\d+")
        self.assertRegex(body["environment_info"][1], r"python/\d+")

    @patch.object(
        Metadata, "session_id", PropertyMock(return_value="unique_session_id")
    )
    @patch.object(
        GenericProvider, "_write_screenshot", MagicMock(return_value="path-to-png-file")
    )
    def test_ignore_region_screenshots_to_the_local_percy_server(self):
        mock_healthcheck()
        mock_screenshot()

        # mock element
        mock_element = MagicMock()
        mock_element.location = {"x": 10, "y": 20}
        mock_element.size = {"width": 200, "height": 400}

        xpaths = ["//path/to/element"]

        # mock call
        self.mock_webdriver.find_element.return_value = mock_element

        # exepected value
        ignored_elements_data = {
            "ignoreElementsData": [
                {
                    "selector": "xpath: //path/to/element",
                    "coOrdinates": {"top": 20, "bottom": 420, "left": 10, "right": 210},
                },
            ]
        }

        percy_screenshot(
            self.mock_webdriver, "screenshot 1", ignore_regions_xpaths=xpaths
        )

        self.assertEqual(httpretty.last_request().path, "/percy/comparison")

        body = httpretty.latest_requests()[1].parsed_body

        # self.assertEqual(s1['name'], 'screenshot 1')
        self.assertRegex(body["client_info"], r"percy-appium-app/\d+")
        self.assertRegex(body["environment_info"][0], r"appium/\d+")
        self.assertDictEqual(body["ignored_elements_data"], ignored_elements_data)
        self.mock_webdriver.find_element.assert_called_with(
            by=AppiumBy.XPATH, value="//path/to/element"
        )
        self.assertEqual(self.mock_webdriver.find_element.call_count, 1)

    def test_throws_error_when_a_driver_is_not_provided_poa(self):
        mock_healthcheck(type="automate")
        with self.assertRaises(Exception):
            percy_screenshot()

    def test_throws_error_when_invalid_driver_provided_poa(self):
        mock_healthcheck(type="automate")
        with self.assertRaises(Exception):
            percy_screenshot("Wrong driver")

    def test_throws_error_when_a_name_is_not_provided_poa(self):
        mock_healthcheck(type="automate")
        with self.assertRaises(Exception):
            percy_screenshot(self.mock_webdriver)

    def test_posts_screenshot_poa(self):
        mock_healthcheck(type="automate")
        mock_poa_screenshot()

        driver = Mock(spec=WebDriver)
        driver.session_id = 'Dummy_session_id'
        driver.capabilities = { 'key': 'value' }
        driver.desired_capabilities = { 'key': 'value' }
        driver.command_executor = Mock()
        driver.command_executor._url = 'https://hub-cloud.browserstack.com/wd/hub'

        element = Mock()
        element.id = 'Dummy_id'

        consider_element = Mock()
        consider_element.id = 'Consider_Dummy_id'
        self.mock_webdriver.capabilities = { 'key': 'value' }
        percy_screenshot(driver, 'Snapshot 1')
        percy_screenshot(driver, 'Snapshot 2', options = {'enable_javascript': True,
                          'ignore_region_appium_elements': [element], 'consider_region_appium_elements' : [consider_element]})

        self.assertEqual(httpretty.last_request().path, '/percy/automateScreenshot')

        s1 = httpretty.latest_requests()[1].parsed_body
        self.assertEqual(s1['snapshotName'], 'Snapshot 1')
        self.assertEqual(s1['sessionId'], driver.session_id)
        self.assertEqual(s1['commandExecutorUrl'], driver.command_executor._url) # pylint: disable=W0212
        self.assertEqual(s1['capabilities'], dict(driver.capabilities))
        self.assertEqual(s1['sessionCapabilites'], dict(driver.desired_capabilities))
        self.assertRegex(s1['client_info'], r'percy-appium-app/\d+')
        self.assertRegex(s1['environment_info'][0], r'appium/\d+')
        self.assertRegex(s1['environment_info'][1], r'python/\d+')
        s2 = httpretty.latest_requests()[-1].parsed_body
        self.assertEqual(s2['snapshotName'], 'Snapshot 2')
        self.assertEqual(s2['options']['enable_javascript'], True)
        self.assertEqual(s2['options']['ignore_region_elements'], ['Dummy_id'])
        self.assertEqual(s2['options']['consider_region_elements'], ['Consider_Dummy_id'])

    def test_posts_screenshot_poa_with_sync(self):
        mock_healthcheck(type="automate")
        mock_poa_screenshot(False, True)

        driver = Mock(spec=WebDriver)
        driver.session_id = 'Dummy_session_id'
        driver.capabilities = { 'key': 'value' }
        driver.desired_capabilities = { 'key': 'value' }
        driver.command_executor = Mock()
        driver.command_executor._url = 'https://hub-cloud.browserstack.com/wd/hub'
        self.mock_webdriver.capabilities = { 'key': 'value' }

        self.assertEqual(percy_screenshot(driver, 'Snapshot 3', options = {'sync': True}), 'sync-data')

if __name__ == "__main__":
    unittest.main()
