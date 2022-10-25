# pylint: disable=[arguments-differ]
import unittest
from unittest.mock import patch
from percy.errors import PlatformNotSupported
from percy.metadata.android_metadata import AndroidMetadata
from percy.metadata.ios_metadata import IOSMetadata
from percy.metadata.metadata_resolver import MetadataResolver


class MetadataResolverTestCase(unittest.TestCase):
    @patch('appium.webdriver.webdriver.WebDriver')
    def setUp(self, mock_webdriver):
        self.mock_android_webdriver = mock_webdriver

    def test_android_resolved(self):
        self.mock_android_webdriver.capabilities = {'platformName': 'Android'}
        resolved_metadata = MetadataResolver.resolve(self.mock_android_webdriver)
        self.assertTrue(isinstance(resolved_metadata, AndroidMetadata))

    def test_ios_resolved(self):
        self.mock_android_webdriver.capabilities = {'platformName': 'iOS'}
        resolved_metadata = MetadataResolver.resolve(self.mock_android_webdriver)
        self.assertTrue(isinstance(resolved_metadata, IOSMetadata))

    def test_unknown_platform_exception(self):
        self.mock_android_webdriver.capabilities = {'platformName': 'Something Random'}
        with self.assertRaises(Exception) as e:
            MetadataResolver.resolve(self.mock_android_webdriver)
        self.assertIsInstance(e.exception, PlatformNotSupported)
