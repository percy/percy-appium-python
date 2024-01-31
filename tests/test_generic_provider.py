# pylint: disable=[arguments-differ, protected-access]
# pylint: disable=R0904
import shutil
import os
import unittest
from unittest.mock import MagicMock, patch, PropertyMock
from appium.webdriver.webdriver import WebDriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException

from percy.lib.cli_wrapper import CLIWrapper
from percy.metadata import AndroidMetadata, Metadata
from percy.providers.generic_provider import GenericProvider
from percy.lib.region import Region
from tests.mocks.mock_methods import android_capabilities


class TestGenericProvider(unittest.TestCase):
    comparison_response = {"comparison": {"id": 123, "url": "https://percy-build-url"}}

    @patch("appium.webdriver.webdriver.WebDriver")
    def setUp(self, mock_webdriver) -> None:
        mock_webdriver.__class__ = WebDriver
        self.existing_dir = "existing-dir"
        os.makedirs(self.existing_dir)

        self.mock_webdriver = mock_webdriver
        self.mock_webdriver.capabilities = android_capabilities
        self.mock_webdriver.orientation = "PorTrait"
        self.mock_webdriver.get_system_bars.return_value = {
            "statusBar": {"height": 10, "width": 20},
            "navigationBar": {"height": 10, "width": 20},
        }
        self.mock_webdriver.get_screenshot_as_png.return_value = b"some random bytes"

        self.android_metadata = AndroidMetadata(self.mock_webdriver)
        self.generic_provider = GenericProvider(
            self.mock_webdriver, self.android_metadata
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.existing_dir)

    def test_get_dir(self):
        dir_created = self.generic_provider._get_dir()
        self.assertEqual(os.listdir(dir_created), [])
        os.removedirs(dir_created)

    @patch.dict(os.environ, {"PERCY_TMP_DIR": "/tmp/percy-apps"})
    def test_get_dir_with_env_var(self):
        dir_created = self.generic_provider._get_dir()
        self.assertEqual(os.listdir(dir_created), [])
        os.removedirs(dir_created)

    def test_get_path(self):
        count = 1000  # Generate count unique paths and check their uniqueness
        png_paths = [
            self.generic_provider._get_path(self.existing_dir) for _ in range(count)
        ]
        self.assertEqual(len(list(set(png_paths))), count)

    def test_write_screenshot(self):
        png_bytes = b"some random bytes"
        filepath = self.generic_provider._write_screenshot(png_bytes, self.existing_dir)
        self.assertTrue(os.path.exists(filepath))

    def test_get_debug_url(self):
        self.assertEqual(self.generic_provider.get_debug_url(), "")

    def test_get_tag(self):
        tag = self.generic_provider._get_tag()
        self.assertIn("name", tag)
        self.assertEqual(tag["name"], self.android_metadata.device_name)
        self.assertIn("os_name", tag)
        self.assertEqual(tag["os_name"], self.android_metadata.os_name)
        self.assertIn("os_version", tag)
        self.assertEqual(tag["os_version"], self.android_metadata.os_version)
        self.assertIn("width", tag)
        self.assertEqual(
            tag["width"], self.android_metadata.device_screen_size["width"]
        )
        self.assertIn("height", tag)
        self.assertEqual(
            tag["height"], self.android_metadata.device_screen_size["height"]
        )
        self.assertIn("orientation", tag)
        self.assertEqual(tag["orientation"], self.android_metadata.orientation.lower())

    def test_get_tag_kwargs(self):
        device_name = "some-device-name"
        tag = self.generic_provider._get_tag(device_name=device_name)
        self.assertIn("name", tag)
        self.assertEqual(tag["name"], device_name)

        orientation = "Some-Orientation"
        tag = self.generic_provider._get_tag(orientation=orientation)
        self.assertIn("orientation", tag)
        self.assertEqual(tag["orientation"], orientation.lower())

    @patch.object(
        Metadata, "session_id", PropertyMock(return_value="unique_session_id")
    )
    def test_get_tiles(self):
        tile = self.generic_provider._get_tiles()[0]
        dict_tile = dict(tile)
        self.assertIn("filepath", dict_tile)
        self.assertIsInstance(dict_tile["filepath"], str)
        self.assertTrue(os.path.exists(dict_tile["filepath"]))
        self.assertIn("status_bar_height", dict_tile)
        self.assertEqual(
            dict_tile["status_bar_height"], self.android_metadata.status_bar_height
        )
        self.assertIn("nav_bar_height", dict_tile)
        self.assertEqual(
            dict_tile["nav_bar_height"], self.android_metadata.navigation_bar_height
        )
        self.assertIn("header_height", dict_tile)
        self.assertEqual(dict_tile["header_height"], 0)
        self.assertIn("footer_height", dict_tile)
        self.assertEqual(dict_tile["footer_height"], 0)
        self.assertIn("fullscreen", dict_tile)
        self.assertFalse(dict_tile["fullscreen"])
        os.remove(tile.filepath)

    def test_get_tiles_kwargs(self):
        status_bar_height, nav_bar_height = 135, 246
        tile = dict(
            self.generic_provider._get_tiles(
                status_bar_height=status_bar_height,
                nav_bar_height=nav_bar_height,
                full_screen=True,
            )[0]
        )
        self.assertIn("status_bar_height", tile)
        self.assertEqual(tile["status_bar_height"], status_bar_height)
        self.assertIn("nav_bar_height", tile)
        self.assertEqual(tile["nav_bar_height"], nav_bar_height)
        self.assertIn("fullscreen", tile)
        self.assertTrue(tile["fullscreen"])

    @patch.object(
        CLIWrapper, "post_screenshots", MagicMock(return_value=comparison_response)
    )
    @patch.object(
        Metadata, "session_id", PropertyMock(return_value="unique_session_id")
    )
    def test_post_screenshots(self):
        tag = self.generic_provider._get_tag()
        tiles = self.generic_provider._get_tiles()
        response = self.generic_provider._post_screenshots(
            "screenshot 1", tag, tiles, "", [], [], False
        )
        self.assertEqual(response, self.comparison_response)

    def test_supports(self):
        self.assertTrue(self.generic_provider.supports("some-dummy-url"))

    @patch.object(
        GenericProvider, "supports", MagicMock(return_value="returned_from_supports")
    )
    def test_supports_mocked(self):
        self.assertEqual(self.generic_provider.supports(""), "returned_from_supports")

    @patch.object(
        GenericProvider,
        "_post_screenshots",
        MagicMock(return_value=comparison_response),
    )
    @patch.object(
        Metadata, "session_id", PropertyMock(return_value="unique_session_id")
    )
    def test_non_app_automate(self):
        response = self.generic_provider.screenshot("screenshot 1")
        self.assertDictEqual(response, self.comparison_response)

    def test_get_device_name(self):
        device_name = self.generic_provider.get_device_name()
        self.assertEqual(device_name, "")

    def test_get_region_object(self):
        # create a mock element object
        mock_element = MagicMock()
        mock_element.location = {"x": 10, "y": 20}
        mock_element.size = {"width": 100, "height": 200}

        # call the function with the mock inputs
        result = self.generic_provider.get_region_object(
            "my-selector", mock_element
        )
        expected_result = {
            "selector": "my-selector",
            "coOrdinates": {"top": 20, "bottom": 220, "left": 10, "right": 110},
        }
        # check the result
        self.assertDictEqual(result, expected_result)

    def test_get_regions_by_xpath(self):
        # create a mock driver object with a mock find_element() method
        mock_element = MagicMock()
        mock_element.location = {"x": 10, "y": 20}
        mock_element.size = {"width": 100, "height": 200}

        self.mock_webdriver.find_element.return_value = mock_element

        expected_result = {
            "selector": "xpath: //path/to/element",
            "coOrdinates": {"top": 20, "bottom": 220, "left": 10, "right": 110},
        }

        # call the function with a mock ignored_elements_array and xpaths
        elements_array = []
        xpaths = ["//path/to/element"]
        self.generic_provider.get_regions_by_xpath(elements_array, xpaths)

        # check the result
        expected_elements_array = [expected_result]
        self.assertEqual(elements_array, expected_elements_array)

        # check that the driver's find_element() method was called twice
        self.mock_webdriver.find_element.assert_called_with(
            by=AppiumBy.XPATH, value="//path/to/element"
        )
        self.assertEqual(self.mock_webdriver.find_element.call_count, 1)

    def test_get_regions_by_xpath_with_non_existing_element(self):
        # mock find_element method of the driver to raise NoSuchElementException
        self.mock_webdriver.find_element.side_effect = NoSuchElementException

        elements_array = []
        xpaths = ["xpath1"]
        self.generic_provider.get_regions_by_xpath(elements_array, xpaths)

        # check the result
        self.assertEqual(len(elements_array), 0)

    def test_get_regions_by_ids(self):
        # create a mock driver object with a mock find_element() method
        mock_element = MagicMock()
        mock_element.location = {"x": 10, "y": 20}
        mock_element.size = {"width": 100, "height": 200}

        self.mock_webdriver.find_element.return_value = mock_element

        expected_result = {
            "selector": "id: some_id",
            "coOrdinates": {"top": 20, "bottom": 220, "left": 10, "right": 110},
        }

        # call the function with a mock elements_array and xpaths
        elements_array = []
        ids = ["some_id"]
        self.generic_provider.get_regions_by_ids(elements_array, ids)

        # check the result
        expected_elements_array = [expected_result]
        self.assertEqual(elements_array, expected_elements_array)

        # check that the driver's find_element() method was called twice
        self.mock_webdriver.find_element.assert_called_with(
            by=AppiumBy.ACCESSIBILITY_ID, value="some_id"
        )
        self.assertEqual(self.mock_webdriver.find_element.call_count, 1)

    def test_get_regions_by_ids_with_non_existing_element(self):
        # mock find_element method of the driver to raise NoSuchElementException
        self.mock_webdriver.find_element.side_effect = NoSuchElementException

        elements_array = []
        ids = ["id1", "id2", "id3"]
        self.generic_provider.get_regions_by_ids(elements_array, ids)

        # check the result
        self.assertEqual(len(elements_array), 0)

    def test_get_regions_by_elements(self):
        # create a mock driver object with a mock find_element() method
        mock_element = MagicMock()
        mock_element.location = {"x": 10, "y": 20}
        mock_element.size = {"width": 100, "height": 200}
        mock_element.get_attribute.return_value = "textView"

        expected_result = {
            "selector": "element: 0 textView",
            "coOrdinates": {"top": 20, "bottom": 220, "left": 10, "right": 110},
        }

        # call the function with a mock elements_array and xpaths
        elements_array = []
        elements = [mock_element]
        self.generic_provider.get_regions_by_elements(
            elements_array, elements
        )

        # check the result
        expected_elements_array = [expected_result]
        self.assertEqual(elements_array, expected_elements_array)

        # check that the driver's find_element() method was called twice
        mock_element.get_attribute.assert_called_with("class")
        self.assertEqual(mock_element.get_attribute.call_count, 1)

    def test_get_regions_by_elements_with_non_existing_element(self):
        # mock find_element method of the driver to raise NoSuchElementException
        mock_element = MagicMock()
        mock_element.get_attribute.side_effect = NoSuchElementException

        elements_array = []
        elements = [mock_element]
        self.generic_provider.get_regions_by_elements(
            elements_array, elements
        )

        # check the result
        self.assertEqual(len(elements_array), 0)

    def test_get_regions_by_location(self):
        # width 1080 height 2280
        valid_ignore_region = Region(100, 200, 200, 300)
        invalid_ignore_region = Region(100, 2390, 200, 300)
        # call the function with mock elements_array and custom_locations
        elements_array = []
        custom_locations = [valid_ignore_region, invalid_ignore_region]
        self.generic_provider.get_regions_by_location(
            elements_array, custom_locations
        )
        # check the result
        expected_elements_array = [
            {
                "selector": "custom ignore region: 0",
                "coOrdinates": {"top": 100, "bottom": 200, "left": 200, "right": 300},
            }
        ]
        self.assertEqual(len(elements_array), 1)
        self.assertEqual(elements_array, expected_elements_array)
