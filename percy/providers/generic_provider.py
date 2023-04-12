import os
import tempfile
from pathlib import Path

from appium.webdriver.webdriver import WebDriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException


from percy.common import log
from percy.lib.cli_wrapper import CLIWrapper
from percy.lib.tile import Tile


class GenericProvider:
    def __init__(self, driver: WebDriver, metadata):
        self.driver = driver
        self.metadata = metadata
        self.debug_url = ''

    @staticmethod
    def supports(_remote_url):
        return True

    def screenshot(self, name, **kwargs):
        tiles = self._get_tiles(**kwargs)
        tag = self._get_tag(**kwargs)
        ignore_regions = self._find_ignored_regions(**kwargs)

        return self._post_screenshots(name, tag, tiles, self.get_debug_url(), ignore_regions)

    def _get_tag(self, **kwargs):
        name = kwargs.get('device_name', self.metadata.device_name)
        os_name = self.metadata.os_name
        os_version = self.metadata.os_version
        width = self.metadata.device_screen_size.get('width', 1)
        height = self.metadata.device_screen_size.get('height', 1)
        orientation = self.metadata.get_orientation(**kwargs).lower()

        return {
            "name": name,
            "os_name": os_name,
            "os_version": os_version,
            "width": width,
            "height": height,
            "orientation": orientation
        }

    def _get_tiles(self, **kwargs):
        fullpage_ss = kwargs.get('fullpage', False)
        if fullpage_ss:
            log('Full page screeshot is only supported on App Automate. Falling back to single page screenshot.')

        png_bytes = self.driver.get_screenshot_as_png()
        directory = self._get_dir()
        path = self._write_screenshot(png_bytes, directory)

        fullscreen = kwargs.get('full_screen', False)
        status_bar_height = kwargs.get('status_bar_height') or self.metadata.status_bar_height
        nav_bar_height = kwargs.get('nav_bar_height') or self.metadata.navigation_bar_height
        header_height = 0
        footer_height = 0
        return [
            Tile(status_bar_height, nav_bar_height, header_height, footer_height, filepath=path, fullscreen=fullscreen)
        ]

    def _find_ignored_regions(self, **kwargs):
        ignored_elements_array = []
        ignore_region_xpaths = kwargs.get("ignore_regions_xpaths", [])
        ignore_region_accessibility_ids = kwargs.get("ignore_region_accessibility_ids", [])
        ignore_region_appium_elements = kwargs.get("ignore_region_appium_elements", [])
        custom_ignore_regions = kwargs.get("custom_ignore_regions", [])
        self.ignore_regions_by_xpaths(ignored_elements_array, ignore_region_xpaths)
        self.ignore_regions_by_ids(ignored_elements_array, ignore_region_accessibility_ids)
        self.ignore_regions_by_elements(ignored_elements_array, ignore_region_appium_elements)
        self.add_custom_ignore_regions(ignored_elements_array, custom_ignore_regions)
        return {
            "ignoreElementsData": ignored_elements_array
        }

    def ignore_element_object(self, selector, element):
        scale_factor = self.metadata.scale_factor
        location = element.location
        size = element.size
        co_ordinates = {
            "top": location["y"] * scale_factor,
            "bottom": (location["y"] + size["height"]) * scale_factor,
            "left": location["x"] * scale_factor,
            "right": (location["x"] + size["width"]) * scale_factor
        }
        ignore_region = {
            "selector": selector,
            "coOrdinates": co_ordinates
        }

        return ignore_region

    def ignore_regions_by_xpaths(self, ignored_elements_array, xpaths):
        for xpath in xpaths:
            try:
                element = self.driver.find_element(by=AppiumBy.XPATH, value=xpath)
                selector = f"xpath: {xpath}"
                ignored_region = self.ignore_element_object(selector, element)
                ignored_elements_array.append(ignored_region)
            except NoSuchElementException as e:
                log(f"Appium Element with xpath: {xpath} not found. Ignoring this xpath.")
                log(e, on_debug=True)

    def ignore_regions_by_ids(self, ignored_elements_array, ids):
        for id in ids:
            try:
                element = self.driver.find_element(by=AppiumBy.ACCESSIBILITY_ID, value=id)
                selector = f"id: {id}"
                ignored_region = self.ignore_element_object(selector, element)
                ignored_elements_array.append(ignored_region)
            except NoSuchElementException as e:
                log(f"Appium Element with id: {id} not found. Ignoring this id.")
                log(e, on_debug=True)

    def ignore_regions_by_elements(self, ignored_elements_array, elements):
        for idx, element in enumerate(elements):
            try:
                class_name = element.get_attribute('class')
                selector = f"element: {idx} {class_name}"
                ignored_region = self.ignore_element_object(selector, element)
                ignored_elements_array.append(ignored_region)
            except NoSuchElementException as e:
                log(f"Correct Element not passed at index {idx}")
                log(e, on_debug=True)

    def add_custom_ignore_regions(self, ignored_elements_array, custom_locations):
        for idx, custom_location in enumerate(custom_locations):
            screen_width = self.metadata.device_screen_size['width']
            screen_height = self.metadata.device_screen_size['height']
            if custom_location.is_valid(screen_height, screen_width):
                ignored_region = {
                    "selector": f"custom ignore region: {idx}",
                    "coOrdinates": {
                        "top": custom_location.top,
                        "bottom": custom_location.bottom,
                        "left": custom_location.left,
                        "right": custom_location.right
                    }
                }
                ignored_elements_array.append(ignored_region)
            else:
                log(f"Values passed in custom ignored region at index: {idx} is not valid")

    @staticmethod
    def _post_screenshots(name, tag, tiles, debug_url, ignored_regions):
        response = CLIWrapper().post_screenshots(name, tag, tiles, debug_url, ignored_regions)
        return response

    def _write_screenshot(self, png_bytes, directory):
        filepath = self._get_path(directory)
        with open(filepath, 'wb') as f:
            f.write(png_bytes)
        return filepath

    def get_debug_url(self):
        return self.debug_url

    def get_device_name(self):
        return ''

    def _get_dir(self):
        dir_path = os.environ.get('PERCY_TMP_DIR') or None
        if dir_path:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            return dir_path
        return tempfile.mkdtemp()

    def _get_path(self, directory):
        suffix = '.png'
        prefix = 'percy-appium-'
        fd, filepath =  tempfile.mkstemp(suffix, prefix, directory)
        os.close(fd)
        return filepath
