# pylint: disable=[abstract-class-instantiated, arguments-differ]
from unittest import TestCase
from unittest.mock import patch, PropertyMock

from percy.metadata.metadata import Metadata


class TestMetadata(TestCase):
    @patch("percy.metadata.metadata.Metadata.__abstractmethods__", set())
    @patch('appium.webdriver.webdriver.WebDriver')
    def setUp(self, mock_webdriver) -> None:
        self.mock_webdriver = mock_webdriver
        self.mock_webdriver.capabilities = PropertyMock()
        self.metadata = Metadata(self.mock_webdriver)

    def test_instantiation(self):
        with self.assertRaises(TypeError) as cm:
            Metadata(self.mock_webdriver)
        self.assertIsInstance(cm.exception, TypeError)

    def test__metadata_properties(self):
        with self.assertRaises(NotImplementedError):
            _device_name = self.metadata.device_name

        with self.assertRaises(NotImplementedError):
            _screen_size = self.metadata.device_screen_size

        with self.assertRaises(NotImplementedError):
            _nav_bar_height = self.metadata.navigation_bar

        with self.assertRaises(NotImplementedError):
            _nav_bar_height = self.metadata.navigation_bar_height

        with self.assertRaises(NotImplementedError):
            _status_bar = self.metadata.status_bar

        with self.assertRaises(NotImplementedError):
            _height = self.metadata.status_bar_height

        with self.assertRaises(NotImplementedError):
            _viewport = self.metadata.viewport

        # Get device info of a device exist in config
        self.assertEqual(self.metadata.device_info, {})
        device_config = self.metadata.get_device_info('iPhone 6')
        self.assertNotEqual(self.metadata.device_info, {})
        self.assertDictEqual(self.metadata.get_device_info('iPhone 6'), device_config)

        # Get device info of a device not exist in config
        with patch('percy.metadata.metadata.log') as mock_log:
            self.metadata.device_info = {}
            self.assertEqual(self.metadata.device_info, {})

            device_name = 'Some Phone 123'
            self.metadata.get_device_info(device_name)
            mock_log.assert_called_once_with(f'{device_name.lower()} does not exist in config.')

    def test__metadata_get_orientation(self):
        orientation = 'PRTRT'
        self.assertEqual(self.metadata.get_orientation(orientation=orientation), orientation)

        orientation = 'prtrt'
        self.assertEqual(self.metadata.get_orientation(orientation=orientation), orientation.upper())

        # Test orientation for kwarg orientation = AUTO, auto, Auto
        orientation = 'OriENTation'
        self.mock_webdriver.orientation = orientation

        self.assertEqual(self.metadata.get_orientation(orientation='AUTO'),
            orientation.upper())
        self.assertEqual(self.metadata.get_orientation(orientation='auto'),
            orientation.upper())
        self.assertEqual(self.metadata.get_orientation(orientation='Auto'),
            orientation.upper())

        # If not provided, should take it from capabilities
        orientation = 'OriEntaTion'
        self.mock_webdriver.capabilities = { 'orientation': orientation }
        self.assertEqual(self.metadata.get_orientation(),
            orientation.upper())

    def test_metadata_session_id(self):
        session_id = 'Some Totally random session ID'
        self.mock_webdriver.session_id = session_id
        self.assertEqual(self.metadata.session_id, session_id)

    def test_metadata_os_version(self):
        capabilities = {'os_version': '10'}
        self.mock_webdriver.capabilities = capabilities
        self.assertEqual(self.metadata.os_version, '10')

        capabilities = {}
        self.mock_webdriver.capabilities = capabilities
        self.assertEqual(self.metadata.os_version, '')

    def test_metadata_value_from_devices_info_for_android(self):
        android_device = 'google pixel 7'
        android_device_info = {'13': {'status_bar': '118', 'nav_bar': '63'}}

        self.metadata._device_name = None
        self.assertEqual(self.metadata.value_from_devices_info('status_bar', android_device, '13'),
            int(android_device_info['13']['status_bar']))

    def test_metadata_value_from_devices_info_for_ios(self):
        ios_device = 'iphone 12 pro max'
        ios_device_info = {'scale_factor': '3', 'status_bar': '47'}
        self.metadata._device_name = None
        self.assertEqual(self.metadata.value_from_devices_info('scale_factor', ios_device),
            int(ios_device_info.get('scale_factor')))
