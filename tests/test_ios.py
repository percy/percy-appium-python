# pylint: disable=[arguments-differ, protected-access]
from unittest import TestCase
from unittest.mock import patch
from appium.webdriver.webdriver import WebDriver

from percy.metadata import IOSMetadata
from tests.mocks.mock_methods import android_capabilities


class TestIOSMetadata(TestCase):
    print('TestIOSMetadata')

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
