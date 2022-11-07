# pylint: disable=[arguments-differ, protected-access]
import copy
import unittest
from unittest.mock import patch, Mock, MagicMock, PropertyMock

from appium.webdriver.webdriver import WebDriver
from percy.errors import DriverNotSupported, UnknownProvider

from percy import percy_screenshot
from percy.lib.app_percy import AppPercy
from percy.lib.cli_wrapper import CLIWrapper
from percy.metadata import IOSMetadata
from percy.providers.app_automate import AppAutomate
from percy.providers.generic_provider import GenericProvider
from percy.metadata import AndroidMetadata
from tests.mocks.mock_methods import android_capabilities, ios_capabilities


class TestAppPercy(unittest.TestCase):
    print('TestAppPercy')
    comparison_response = {'link': 'https://snapshot_url', 'success': True}

    @patch('appium.webdriver.webdriver.WebDriver')
    def setUp(self, mock_webdriver):
        mock_webdriver.__class__ = WebDriver
        self.mock_android_webdriver = copy.deepcopy(mock_webdriver)
        self.mock_android_webdriver.capabilities = android_capabilities
        self.mock_android_webdriver.orientation = 'PORTRAIT'
        self.mock_android_webdriver.get_system_bars.return_value = {'statusBar': {'height': 10, 'width': 20},
                                                                    'navigationBar': {'height': 10, 'width': 20}}

        self.mock_ios_webdriver = copy.deepcopy(mock_webdriver)
        self.mock_ios_webdriver.capabilities = ios_capabilities
        self.mock_ios_webdriver.orientation = 'PORTRAIT'

    def tearDown(self) -> None:
        self.mock_android_webdriver.capabilities['desired']['percy:options'] = {'enabled': True}
        self.mock_android_webdriver.capabilities['percy:options'] = {'enabled': True}

    @patch.object(AndroidMetadata, 'execute_script', MagicMock(return_value='{"browser_url": "https://browser_ur", "device": "Google Pixel 4"}'))
    @patch.object(CLIWrapper, 'post_screenshots', MagicMock(return_value=comparison_response))
    @patch.object(GenericProvider, '_write_screenshot', MagicMock(return_value='path-to-png-file'))
    @patch.object(AppAutomate, 'get_debug_url', MagicMock(return_value='https://mocked-app-automate-session-url'))
    @patch.object(AppAutomate, 'execute_percy_screenshot_begin', MagicMock(return_value=None))
    @patch.object(AppAutomate, 'execute_percy_screenshot_end', MagicMock(return_value=None))
    def test_android_on_app_automate(self):
        with patch('percy.metadata.AndroidMetadata.remote_url', new_callable=PropertyMock) as mock_remote_url:
            mock_remote_url.return_value = 'url-of-browserstack-cloud'
            app_percy = AppPercy(self.mock_android_webdriver)
            response = app_percy.screenshot('screenshot 1')
            self.assertEqual(response, self.comparison_response)
            self.assertTrue(isinstance(app_percy.metadata, AndroidMetadata))
            self.assertTrue(isinstance(app_percy.provider, AppAutomate))

    @patch.object(GenericProvider, '_write_screenshot', MagicMock(return_value='path-to-png-file'))
    @patch.object(CLIWrapper, 'post_screenshots', MagicMock(return_value=comparison_response))
    def test_android_on_non_app_automate(self):
        with patch('percy.metadata.AndroidMetadata.remote_url', new_callable=PropertyMock) as mock_remote_url:
            mock_remote_url.return_value = ''
            app_percy = AppPercy(self.mock_android_webdriver)
            response = app_percy.screenshot('screenshot 2')
            self.assertEqual(response, self.comparison_response)
            self.assertTrue(isinstance(app_percy.metadata, AndroidMetadata))
            self.assertTrue(isinstance(app_percy.provider, GenericProvider))

    @patch.object(IOSMetadata, 'execute_script',
    MagicMock(side_effect=[{'top': 14, 'height': 1500},
                           {'top': 40, 'height': 1200}]))
    @patch.object(AppAutomate, 'get_debug_url', MagicMock(return_value='https://mocked-app-automate-session-url'))
    @patch.object(GenericProvider, '_write_screenshot', MagicMock(return_value='path-to-png-file'))
    @patch.object(CLIWrapper, 'post_screenshots', MagicMock(return_value=comparison_response))
    @patch.object(AppAutomate, 'execute_percy_screenshot_begin', MagicMock(return_value=None))
    @patch.object(AppAutomate, 'execute_percy_screenshot_end', MagicMock(return_value=None))
    def test_ios_on_app_automate(self):
        with patch('percy.metadata.IOSMetadata.remote_url', new_callable=PropertyMock) as mock_remote_url:
            mock_remote_url.return_value = 'url-of-browserstack-cloud'
            app_percy = AppPercy(self.mock_ios_webdriver)
            response = app_percy.screenshot('screenshot 1')
            self.assertEqual(response, self.comparison_response)
            self.assertTrue(isinstance(app_percy.metadata, IOSMetadata))
            self.assertTrue(isinstance(app_percy.provider, AppAutomate))

    @patch.object(GenericProvider, '_write_screenshot', MagicMock(return_value='path-to-png-file'))
    @patch.object(CLIWrapper, 'post_screenshots', MagicMock(return_value=comparison_response))
    def test_ios_on_non_app_automate(self):
        with patch('percy.metadata.IOSMetadata.remote_url', new_callable=PropertyMock) as mock_remote_url:
            mock_remote_url.return_value = ''
            app_percy = AppPercy(self.mock_ios_webdriver)
            response = app_percy.screenshot('screenshot 2')
            self.assertEqual(response, self.comparison_response)
            self.assertTrue(isinstance(app_percy.metadata, IOSMetadata))
            self.assertTrue(isinstance(app_percy.provider, GenericProvider))

    def test_screenshot_with_percy_options_disabled(self):
        self.mock_android_webdriver.capabilities['percy:options'] = {'enabled': False}

        app_percy = AppPercy(self.mock_android_webdriver)
        self.assertIsNone(app_percy.screenshot('screenshot 1'))

    @patch('percy.screenshot.log')
    @patch.object(AppPercy, 'screenshot', MagicMock(side_effect = Exception('RealException')))
    @patch.object(CLIWrapper, 'is_percy_enabled', MagicMock(return_value=True))
    def test_percy_options_ignore_errors(self, _mocked_log):
        self.mock_android_webdriver.capabilities['percy:options'] = {'ignoreErrors': False}
        self.assertRaises(Exception, percy_screenshot, self.mock_android_webdriver, 'screenshot')
        _mocked_log.assert_called_once_with('Could not take screenshot "screenshot"')

    @patch('percy.screenshot.log')
    @patch.object(CLIWrapper, 'is_percy_enabled', MagicMock(return_value=True))
    def test_percy_options_ignore_errors_not_raise(self, _mock_log):
        with patch.object(AppPercy, 'screenshot') as mock_screenshot:
            exception = Exception('Some Exception')
            mock_screenshot.side_effect = exception
            self.mock_android_webdriver.capabilities['percy:options'] = {'ignoreErrors': True}
            percy_screenshot(self.mock_android_webdriver, 'screenshot')
            _mock_log.assert_called_with(exception, on_debug=True)

    @patch.object(GenericProvider, 'supports', MagicMock(return_value=False))
    def test_invalid_provider(self):
        mock_command_executor = Mock()
        mock_command_executor._url.return_value = ''
        self.mock_android_webdriver.command_executor = mock_command_executor

        with self.assertRaises(Exception) as cm:
            _provider = AppPercy(self.mock_android_webdriver).provider
        self.assertIsInstance(cm.exception, UnknownProvider)

    def test_invalid_driver(self):
        with self.assertRaises(Exception) as e:
            AppPercy(Mock())
        self.assertIsInstance(e.exception, DriverNotSupported)
