# pylint: disable=[abstract-class-instantiated, arguments-differ]
from unittest import TestCase
from unittest.mock import patch, PropertyMock

from percy.metadata.metadata import Metadata


class TestMetadata(TestCase):
    @patch('appium.webdriver.webdriver.WebDriver')
    def setUp(self, mock_webdriver) -> None:
        self.mock_webdriver = mock_webdriver
        self.mock_webdriver.capabilities = PropertyMock()

    def test_instantiation(self):
        with self.assertRaises(TypeError) as cm:
            Metadata(self.mock_webdriver)
        self.assertIsInstance(cm.exception, TypeError)

    @patch("percy.metadata.metadata.Metadata.__abstractmethods__", set())
    def test_base_metadata_properties(self):
        base_metadata = Metadata(self.mock_webdriver)

        with self.assertRaises(NotImplementedError):
            _device_name = base_metadata.device_name

        with self.assertRaises(NotImplementedError):
            _screen_size = base_metadata.device_screen_size

        with self.assertRaises(NotImplementedError):
            _nav_bar_height = base_metadata.navigation_bar

        with self.assertRaises(NotImplementedError):
            _nav_bar_height = base_metadata.navigation_bar_height

        with self.assertRaises(NotImplementedError):
            _status_bar = base_metadata.status_bar

        with self.assertRaises(NotImplementedError):
            _height = base_metadata.status_bar_height

        with self.assertRaises(NotImplementedError):
            _viewport = base_metadata.viewport

        # Get device info of a device exist in config
        self.assertEqual(base_metadata.device_info, {})
        device_config = base_metadata.get_device_info('iPhone 6')
        self.assertNotEqual(base_metadata.device_info, {})
        self.assertDictEqual(base_metadata.get_device_info('iPhone 6'), device_config)

        # Get device info of a device not exist in config
        with patch('percy.metadata.metadata.log') as mock_log:
            base_metadata.device_info = {}
            self.assertEqual(base_metadata.device_info, {})

            device_name = 'Some Phone 123'
            base_metadata.get_device_info(device_name)
            mock_log.assert_called_once_with(f'{device_name.lower()} does not exist in config.')

    @patch("percy.metadata.metadata.Metadata.__abstractmethods__", set())
    def test_base_metadata_get_orientation(self):
        base_metadata = Metadata(self.mock_webdriver)
        orientation = 'PRTRT'
        self.assertEqual(base_metadata.get_orientation(orientation=orientation), orientation)

        orientation = 'prtrt'
        self.assertEqual(base_metadata.get_orientation(orientation=orientation), orientation.upper())

        # Test orientation for kwarg orientation = AUTO, auto, Auto
        orientation = 'OriENTation'
        self.mock_webdriver.orientation = orientation
        base_metadata = Metadata(self.mock_webdriver)
        self.assertEqual(base_metadata.get_orientation(orientation='AUTO'),
            orientation.upper())
        self.assertEqual(base_metadata.get_orientation(orientation='auto'),
            orientation.upper())
        self.assertEqual(base_metadata.get_orientation(orientation='Auto'),
            orientation.upper())

        # If not provided, should take it from capabilities
        orientation = 'OriEntaTion'
        self.mock_webdriver.capabilities = { 'orientation': orientation }
        self.assertEqual(base_metadata.get_orientation(),
            orientation.upper())
