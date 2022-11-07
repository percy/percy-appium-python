# pylint: disable=[abstract-class-instantiated]
from unittest import TestCase
from unittest.mock import Mock, patch

from percy.metadata.metadata import Metadata


class TestBaseMetadata(TestCase):
    print('TestBaseMetadata')
    def test_instantiation(self):
        with self.assertRaises(TypeError) as cm:
            Metadata(Mock())
        self.assertIsInstance(cm.exception, TypeError)

    @patch("percy.metadata.metadata.Metadata.__abstractmethods__", set())
    def test_base_metadata_properties(self):
        base_metadata = Metadata(Mock())
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
