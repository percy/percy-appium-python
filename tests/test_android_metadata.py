# pylint: disable=[arguments-differ]
from unittest import TestCase
from unittest.mock import Mock, patch, PropertyMock
from appium.webdriver.webdriver import WebDriver
from percy.metadata import AndroidMetadata, Metadata
from tests.mocks.mock_methods import android_capabilities


class TestAndroidMetadata(TestCase):
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

    @patch.object(Metadata, 'session_id', PropertyMock(return_value='unique_session_id'))
    def test_get_system_bars(self):
        system_bars = self.android_metadata.get_system_bars()
        self.assertEqual(system_bars['statusBar']['height'], 83)
        self.assertEqual(system_bars['navigationBar']['height'], 44)

        self.mock_webdriver.capabilities['viewportRect'] = None
        mock_get_system_bars = Mock()
        self.mock_webdriver.get_system_bars = mock_get_system_bars
        AndroidMetadata(self.mock_webdriver).get_system_bars()
        mock_get_system_bars.assert_called_once()


    def test_status_bar(self):
        mock_get_system_bars = {'statusBar': {'height': 1}}
        self.android_metadata.get_system_bars = Mock(return_value=mock_get_system_bars)
        self.assertEqual(self.android_metadata.status_bar_height, 0)

    def test_navigation_bar(self):
        mock_get_system_bars = {'navigationBar': {'height': 1}}
        self.android_metadata.get_system_bars = Mock(return_value=mock_get_system_bars)
        self.assertEqual(self.android_metadata.navigation_bar_height, 0)

    def test_scale_factor(self):
        self.assertEqual(self.android_metadata.scale_factor, 1)
