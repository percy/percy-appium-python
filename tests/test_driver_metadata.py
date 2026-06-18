# pylint: disable=[abstract-class-instantiated, arguments-differ]
import unittest
from unittest.mock import patch
from appium.webdriver.webdriver import WebDriver

from percy.metadata.driver_metadata import DriverMetaData

class TestDriverMetadata(unittest.TestCase):
    @patch('appium.webdriver.webdriver.WebDriver')
    @patch('percy.lib.cache.Cache.CACHE', {})
    def setUp(self, mock_appium) -> None:
        mock_appium.__class__ = WebDriver
        self.mock_webdriver = mock_appium
        self.mock_webdriver.orientation = 'PORTRAIT'
        self.mock_webdriver.session_id = 'session_id_123'
        self.mock_webdriver.command_executor._url = 'https://example-hub:4444/wd/hub' # pylint: disable=W0212
        self.mock_webdriver.command_executor._client_config = None # pylint: disable=W0212
        self.mock_webdriver.capabilities = {
            'platform': 'chrome_android',
            'browserVersion': '115.0.1'
        }

        self.mock_webdriver.desired_capabilities = {
            'platform': 'chrome_android',
            'browserVersion': '115.0.1',
            'session_name': 'abc'
          }

        self.metadata = DriverMetaData(self.mock_webdriver)

    @patch('percy.lib.cache.Cache.CACHE', {})
    def test_session_id(self):
        session_id = 'session_id_123'
        self.mock_webdriver.session_id = session_id
        self.assertEqual(self.metadata.session_id, session_id)

    @patch('percy.lib.cache.Cache.CACHE', {})
    def test_command_executor_url(self):
        url = 'https://example-hub:4444/wd/hub'
        self.assertEqual(self.metadata.command_executor_url, url)

    @patch('percy.lib.cache.Cache.CACHE', {})
    def test_command_executor_url_with_client_config(self):
        # New Appium-Python-Client (>3) / Selenium 4.x exposes the address via
        # command_executor._client_config.remote_server_addr
        url = 'https://new-style-hub:4444/wd/hub'
        self.mock_webdriver.command_executor._client_config = \
            type('Config', (), {'remote_server_addr': url})() # pylint: disable=W0212
        self.assertEqual(self.metadata.command_executor_url, url)

    @patch('percy.lib.cache.Cache.CACHE', {})
    def test_command_executor_url_fallback_to_url(self):
        # Older clients only expose command_executor._url
        self.mock_webdriver.command_executor._client_config = None # pylint: disable=W0212
        self.mock_webdriver.command_executor._url = 'https://old-style-hub:4444/wd/hub' # pylint: disable=W0212
        self.assertEqual(self.metadata.command_executor_url, 'https://old-style-hub:4444/wd/hub')

    @patch('percy.lib.cache.Cache.CACHE', {})
    def test_capabilities(self):
        capabilities = {
            'platform': 'chrome_android',
            'browserVersion': '115.0.1'
        }

        self.mock_webdriver.capabilities = capabilities
        self.assertDictEqual(self.metadata.capabilities, capabilities)
