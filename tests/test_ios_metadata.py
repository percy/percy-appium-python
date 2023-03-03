# pylint: disable=[arguments-differ, protected-access]
from unittest import TestCase
from unittest.mock import patch, MagicMock, PropertyMock
from appium.webdriver.webdriver import WebDriver

from percy.metadata import IOSMetadata, Metadata
from tests.mocks.mock_methods import android_capabilities


class TestIOSMetadata(TestCase):
    @patch('appium.webdriver.webdriver.WebDriver')
    def setUp(self, mock_appium) -> None:
        mock_appium.__class__ = WebDriver
        self.mock_webdriver = mock_appium
        self.mock_webdriver.capabilities = android_capabilities
        self.mock_webdriver.orientation = 'PORTRAIT'
        self.ios_metadata = IOSMetadata(self.mock_webdriver)

    def test_ios_execute_script(self):
        command = 'some dummy command'
        output = 'some output'
        self.mock_webdriver.execute_script.return_value = output

        response = self.ios_metadata.execute_script(command)
        self.mock_webdriver.execute_script.assert_called_with(command)
        self.assertEqual(response, output)

    def test_remote_url(self):
        self.mock_webdriver.command_executor._url = 'some-remote-url'
        self.assertEqual(self.ios_metadata.remote_url, 'some-remote-url')

    @patch.object(Metadata, 'session_id', PropertyMock(return_value='unique_session_id'))
    def test_get_window_size(self):
        height, width = 100, 100
        window_size = {'height': height, 'width': width}
        self.mock_webdriver.get_window_size.return_value = window_size
        self.assertDictEqual(self.ios_metadata._window_size, {})
        fetched_window_size = self.ios_metadata.get_window_size()
        self.assertDictEqual(window_size, fetched_window_size)

    @patch.object(IOSMetadata, 'execute_script',  MagicMock(side_effect = Exception('RealException')))
    @patch.object(Metadata, 'session_id', PropertyMock(return_value='unique_session_id'))
    @patch('percy.lib.cache.Cache.CACHE', {})
    @patch('percy.metadata.ios_metadata.log')
    def test_viewport_exception(self, mock_log):
        _viewport = self.ios_metadata.viewport
        mock_log.assert_called_once_with('Could not use viewportRect; using static config', on_debug=True)

    @patch.object(IOSMetadata, 'device_name',  PropertyMock(return_value = 'iPhone 6'))
    @patch.object(IOSMetadata, 'execute_script',  MagicMock(side_effect = Exception('RealException')))
    @patch.object(Metadata, 'session_id', PropertyMock(return_value='unique_session_id'))
    @patch('percy.lib.cache.Cache.CACHE', {})
    def test_device_screen_size(self):
        self.mock_webdriver.get_window_size.return_value = {'height': 100, 'width': 100}
        device_screen_size = self.ios_metadata.device_screen_size
        self.assertDictEqual(device_screen_size, {'height': 200, 'width': 200})

    @patch.object(IOSMetadata, 'device_name',  PropertyMock(return_value = 'iPhone 6'))
    @patch.object(IOSMetadata, 'os_version',  PropertyMock(return_value = '10.0'))
    @patch.object(IOSMetadata, 'execute_script',  MagicMock(side_effect = Exception('RealException')))
    @patch.object(Metadata, 'session_id', PropertyMock(return_value='unique_session_id'))
    @patch('percy.lib.cache.Cache.CACHE', {})
    def test_status_bar(self):
        status_bar = self.ios_metadata.status_bar
        self.assertDictEqual(status_bar, {'height': 40})

    @patch.object(IOSMetadata, 'device_name',  PropertyMock(return_value = 'iPhone 6'))
    def test_scale_factor_present_in_devices_json(self):
        self.assertEqual(self.ios_metadata.scale_factor, 2)

    @patch.object(Metadata, 'session_id', PropertyMock(return_value='unique_session_id'))
    @patch.object(IOSMetadata, 'device_name',  PropertyMock(return_value = 'iPhone 14'))
    def test_scale_factor_not_present_in_devices_json(self):
        window_size = {'height': 100, 'width': 100}
        self.mock_webdriver.get_window_size.return_value = window_size
        self.mock_webdriver.execute_script.return_value = {'height': 100, 'width': 200}
        self.assertEqual(self.ios_metadata.scale_factor, 2)
