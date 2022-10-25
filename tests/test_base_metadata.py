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
