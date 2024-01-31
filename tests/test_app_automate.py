# pylint: disable=[arguments-differ, protected-access]
import unittest
import os
from unittest.mock import MagicMock, patch, PropertyMock
from appium.webdriver.webdriver import WebDriver
from percy.providers.app_automate import AppAutomate
from percy.providers.generic_provider import GenericProvider
from percy.metadata import AndroidMetadata, Metadata
from tests.mocks.mock_methods import android_capabilities

class TestAppAutomate(unittest.TestCase):
    comparison_response = {'success': True, 'link': 'https://snapshots-url'}

    @patch('appium.webdriver.webdriver.WebDriver')
    def setUp(self, mock_webdriver) -> None:
        mock_webdriver.__class__ = WebDriver
        self.mock_webdriver = mock_webdriver
        self.mock_webdriver.capabilities = android_capabilities
        self.mock_webdriver.orientation = 'PORTRAIT'
        self.mock_webdriver.get_system_bars.return_value = {
            'statusBar': {'height': 10, 'width': 20},
            'navigationBar': {'height': 10, 'width': 20}
        }
        self.metadata = AndroidMetadata(self.mock_webdriver)
        self.app_automate = AppAutomate(self.mock_webdriver, self.metadata)

    @patch.object(Metadata, 'session_id', PropertyMock(return_value='unique_session_id'))
    def test_app_automate_get_debug_url(self):
        self.app_automate.set_debug_url({'deviceName': 'Google Pixel 4', 'osVersion': '12.0', 'buildHash': 'abc', 'sessionHash': 'def'})
        debug_url = self.app_automate.get_debug_url()
        self.assertEqual(debug_url, 'https://app-automate.browserstack.com/dashboard/v2/builds/abc/sessions/def')

    def test_app_automate_supports_with_correct_url(self):
        app_automate_session = self.app_automate.supports('https://hub-cloud.browserstack.com/wd/hub')
        self.assertEqual(app_automate_session, True)

    def test_app_automate_supports_with_incorrect_url(self):
        app_automate_session = self.app_automate.supports('https://hub-cloud.generic.com/wd/hub')
        self.assertEqual(app_automate_session, False)

    @patch.dict(os.environ, {"AA_DOMAIN": "bsstag"})
    def test_app_automate_supports_with_AA_DOMAIN(self):
        app_automate_session = self.app_automate.supports('bsstag.com')
        self.assertEqual(app_automate_session, True)

    @patch('percy.providers.app_automate.log')
    def test_app_automate_execute_percy_screenshot_begin(self, _mocked_log):
        self.mock_webdriver.execute_script.return_value = {}
        self.assertIsNone(self.app_automate.execute_percy_screenshot_begin('Screebshot 1'))
        self.mock_webdriver.execute_script.assert_called()

    def test_app_automate_execute_percy_screenshot_end(self):
        self.mock_webdriver.execute_script.return_value = {}
        self.assertIsNone(self.app_automate.execute_percy_screenshot_end('Screenshot 1', self.comparison_response['link'], 'success', False))
        self.mock_webdriver.execute_script.assert_called()

    def test_app_automate_execute_percy_screenshot(self):
        self.mock_webdriver.execute_script.return_value = '{"result": "result"}'
        self.app_automate.execute_percy_screenshot(1080, 'singlepage', 5)
        self.mock_webdriver.execute_script.assert_called()

    @patch('percy.providers.app_automate.log')
    def test_execute_percy_screenshot_end_throws_error(self, mock_log):
        self.mock_webdriver.execute_script.side_effect = Exception('SomeException')
        self.app_automate.execute_percy_screenshot_end('Screenshot 1', 'snapshot-url', 'success', None)
        mock_log.assert_called()

    @patch.object(Metadata, 'session_id', PropertyMock(return_value='unique_session_id'))
    @patch.object(GenericProvider, 'screenshot', MagicMock(return_value={'link': 'https://link'}))
    def test_execute_percy_screenshot_end(self):
        self.app_automate.execute_percy_screenshot_begin = MagicMock(return_value={'deviceName': 'abc', 'osVersion': '123'})
        mock_screenshot_end = MagicMock(return_value=None)
        self.app_automate.execute_percy_screenshot_end = mock_screenshot_end
        self.app_automate.screenshot('name')
        mock_screenshot_end.assert_called_once_with('name', 'https://link', 'success', None)

        # check that code doesnt throw if begin fails
        self.app_automate.execute_percy_screenshot_begin = MagicMock(return_value=None)
        self.app_automate.screenshot('name')

        with self.assertRaises(Exception) as e:
            mock_screenshot_end.side_effect = Exception('RandomException')
            self.app_automate.screenshot('name')
        mock_screenshot_end.assert_called_with('name', 'https://link', 'failure', None, str(e.exception))

    @patch.object(AppAutomate, 'execute_percy_screenshot', MagicMock(return_value={
        "result":"[{\"sha\":\"sha-25568755\",\"status_bar\":null,\"nav_bar\":null,\"header_height\":120,\"footer_height\":80,\"index\":0}]"
    }))
    @patch.object(Metadata, 'session_id', PropertyMock(return_value='unique_session_id'))
    @patch.object(AndroidMetadata, 'device_screen_size', PropertyMock(return_value={'width': 1080, 'height': 1920}))
    @patch.object(AndroidMetadata, 'navigation_bar_height', PropertyMock(return_value=150))
    @patch.object(AndroidMetadata, 'status_bar_height', PropertyMock(return_value=100))
    def test_get_tiles(self):
        result = self.app_automate._get_tiles(fullpage=True)[0]
        self.assertEqual(result.sha, 'sha')
        self.assertEqual(result.status_bar_height, 100)
        self.assertEqual(result.nav_bar_height, 150)
        self.assertEqual(result.header_height, 120)
        self.assertEqual(result.footer_height, 80)
