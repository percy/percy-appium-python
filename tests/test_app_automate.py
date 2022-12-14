# pylint: disable=[arguments-differ, protected-access]
import unittest
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

    @patch('percy.providers.app_automate.log')
    def test_app_automate_execute_percy_screenshot_begin(self, _mocked_log):
        self.mock_webdriver.execute_script.return_value = {}
        self.assertIsNone(self.app_automate.execute_percy_screenshot_begin('Screebshot 1'))
        self.mock_webdriver.execute_script.assert_called()

    def test_app_automate_execute_percy_screenshot_end(self):
        self.mock_webdriver.execute_script.return_value = {}
        self.assertIsNone(self.app_automate.execute_percy_screenshot_end('Screenshot 1', self.comparison_response['link'], 'success'))
        self.mock_webdriver.execute_script.assert_called()

    @patch('percy.providers.app_automate.log')
    def test_execute_percy_screenshot_end_throws_error(self, mock_log):
        self.mock_webdriver.execute_script.side_effect = Exception('SomeException')
        self.app_automate.execute_percy_screenshot_end('Screenshot 1', 'snapshot-url', 'success')
        mock_log.assert_called()

    @patch.object(Metadata, 'session_id', PropertyMock(return_value='unique_session_id'))
    @patch.object(GenericProvider, 'screenshot', MagicMock(return_value={'link': 'https://link'}))
    def test_execute_percy_screenshot_end(self):
        self.app_automate.execute_percy_screenshot_begin = MagicMock()
        mock_screenshot_end = MagicMock()
        self.app_automate.execute_percy_screenshot_end = mock_screenshot_end
        self.app_automate.screenshot('name')
        mock_screenshot_end.assert_called_once_with('name', 'https://link', 'success')

        with self.assertRaises(Exception) as e:
            mock_screenshot_end.side_effect = Exception('RandomException')
            self.app_automate.screenshot('name')
        mock_screenshot_end.assert_called_with('name', 'https://link', 'failure', str(e.exception))
