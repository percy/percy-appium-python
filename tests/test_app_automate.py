# pylint: disable=[arguments-differ, protected-access]
import unittest
from unittest.mock import MagicMock, patch
import time
from appium.webdriver.webdriver import WebDriver
from percy.providers.app_automate import AppAutomate
from percy.metadata import AndroidMetadata
from tests.mocks.mock_methods import android_capabilities


class TestAppAutomate(unittest.TestCase):
    print('TestAppAutomate')
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
    def test_app_automate_get_debug_url(self):
        debug_url = self.app_automate.get_debug_url()
        self.assertEqual(debug_url, 'app_automate_session_url')

    @patch('percy.providers.app_automate.log')
    def test_app_automate_execute_percy_screenshot_begin(self, _mocked_log):
        self.mock_webdriver.execute_script.return_value = {}
        self.assertIsNone(self.app_automate.execute_percy_screenshot_begin())
        self.mock_webdriver.execute_script.assert_called()

    @patch('percy.providers.app_automate.log')
    def test_execute_percy_screenshot_begin_throws_error(self, mocked_log):
        self.mock_webdriver.execute_script.side_effect = Exception('SomeException')
        self.assertTrue(self.app_automate._marked_percy_session)
        self.app_automate.execute_percy_screenshot_begin()
        self.assertFalse(self.app_automate._marked_percy_session)
        mocked_log.assert_called()

    def test_app_automate_execute_percy_screenshot_end(self):
        self.mock_webdriver.execute_script.return_value = {}
        self.assertIsNone(self.app_automate.execute_percy_screenshot_end(self.comparison_response['link']))
        self.mock_webdriver.execute_script.assert_called()

    @patch('percy.providers.app_automate.log')
    def test_execute_percy_screenshot_end_throws_error(self, mocked_log):
        self.mock_webdriver.execute_script.side_effect = Exception('SomeException')
        self.app_automate.execute_percy_screenshot_end('snapshot-url')
        mocked_log.assert_called()

    @patch.object(AndroidMetadata, 'execute_script', MagicMock(return_value='{"browser_url": "app_automate_session_id"}'))
    def test_get_cached_session_id(self):
        self.app_automate._set_session_cache('https://app-automate-session-url')
        cached_session_url = self.app_automate._get_cached_session()
        self.assertEqual(cached_session_url, 'https://app-automate-session-url')

    def test_app_automate_cache_clean(self):
        self.app_automate.CACHE_PERIOD = 2  # 2 seconds
        self.app_automate._set_session_cache('value-for-session-id')
        time.sleep(3)
        self.app_automate._clean_cache()
        self.assertListEqual(list(self.app_automate.SESSION_CACHE.keys()), [])
