# pylint: disable=[arguments-differ, protected-access]
import unittest
from unittest.mock import MagicMock, patch, PropertyMock
from appium.webdriver.webdriver import WebDriver
from percy.providers.app_automate import AppAutomate
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

    @patch.object(AppAutomate, 'screenshot', MagicMock(return_value=comparison_response))
    def test_app_automate_screenshot(self):
        response = self.app_automate.screenshot('screenshot 1')
        self.assertDictEqual(response, self.comparison_response)

    @patch.object(AndroidMetadata, 'execute_script', MagicMock(return_value='{"browser_url": "app_automate_session_url"}'))
    @patch.object(AndroidMetadata, 'execute_script', MagicMock(return_value='{"browser_url": "app_automate_session_url"}'))
    @patch.object(Metadata, 'session_id', PropertyMock(return_value='unique_session_id'))
    def test_app_automate_get_debug_url(self):
        debug_url = self.app_automate.get_debug_url()
        self.assertEqual(debug_url, 'app_automate_session_url')

    @patch('percy.providers.app_automate.log')
    def test_app_automate_execute_percy_screenshot_begin(self, _mocked_log):
        self.mock_webdriver.execute_script.return_value = {}
        self.assertIsNone(self.app_automate.execute_percy_screenshot_begin())
        self.mock_webdriver.execute_script.assert_called()

    @patch('percy.providers.app_automate.log')
    def test_execute_percy_screenshot_begin_throws_error(self, mock_log):
        self.mock_webdriver.execute_script.side_effect = Exception('SomeException')
        self.assertTrue(self.app_automate._marked_percy_session)
        self.app_automate.execute_percy_screenshot_begin()
        self.assertFalse(self.app_automate._marked_percy_session)
        mock_log.assert_called()

    def test_app_automate_execute_percy_screenshot_end(self):
        self.mock_webdriver.execute_script.return_value = {}
        self.assertIsNone(self.app_automate.execute_percy_screenshot_end(self.comparison_response['link']))
        self.mock_webdriver.execute_script.assert_called()

    @patch('percy.providers.app_automate.log')
    def test_execute_percy_screenshot_end_throws_error(self, mock_log):
        self.mock_webdriver.execute_script.side_effect = Exception('SomeException')
        self.app_automate.execute_percy_screenshot_end('snapshot-url')
        mock_log.assert_called()

    @patch('percy.lib.cache.Cache.CACHE', {})
    @patch.object(AndroidMetadata, 'execute_script', MagicMock(side_effect=TimeoutError('Connection Refused')))
    @patch.object(Metadata, 'session_id', PropertyMock(return_value='unique_session_id'))
    @patch('percy.providers.app_automate.log')
    def test_get_session_details(self, mock_log):
        self.app_automate.get_session_details()
        mock_log.assert_called()
