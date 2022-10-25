# pylint: disable=[arguments-differ]
from unittest import TestCase
from unittest.mock import patch
from appium.webdriver.webdriver import WebDriver
from percy.metadata import AndroidMetadata
from tests.mocks.mock_methods import android_capabilities


class TestAndroidMetadata(TestCase):
    print('TestAndroidMetadata')

    @patch('appium.webdriver.webdriver.WebDriver')
    def setUp(self, mock_appium) -> None:
        mock_appium.__class__ = WebDriver
        self.mock_webdriver = mock_appium
        self.mock_webdriver.capabilities = android_capabilities
        self.mock_webdriver.orientation = 'PORTRAIT'
        self.android_metadata = AndroidMetadata(self.mock_webdriver)

    def test_android_execute_script(self):
        command = 'some dummy command'
        output = 'some output'
        self.mock_webdriver.execute_script.return_value = output

        response = self.android_metadata.execute_script(command)
        self.mock_webdriver.execute_script.assert_called_with(command)
        self.assertEqual(response, output)

    def test_viewport(self):
        viewport = {'left': 0, 'top': 84, 'width': 1440, 'height': 2708}
        self.mock_webdriver.capabilities['viewportRect'] = viewport
        self.assertDictEqual(self.android_metadata.viewport, viewport)
