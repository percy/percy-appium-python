import os
import tempfile

from appium.webdriver.webdriver import WebDriver

from percy.lib.cli_wrapper import CLIWrapper
from percy.lib.tile import Tile


class GenericProvider:
    def __init__(self, driver: WebDriver, metadata) -> None:
        self.driver = driver
        self.metadata = metadata

    @staticmethod
    def supports(_remote_url):
        return True

    def screenshot(self, name, fullscreen, debug_url=''):
        tiles = self._get_tiles(fullscreen)
        tag = self._get_tag()
        return self._post_screenshots(name, tag, tiles, debug_url)

    def _get_tag(self):
        return {
            "name": self.metadata.device_name,
            "os-name": self.metadata.os_name,
            "os-version": self.metadata.os_version,
            "width": self.metadata.device_screen_size['width'],
            "height": self.metadata.device_screen_size['height'],
            "orientation": self.metadata.orientation.lower()
        }

    def _get_tiles(self, fullscreen=False):
        png_bytes = self.driver.get_screenshot_as_png()
        directory = self._get_dir()
        path = self._write_screenshot(png_bytes, directory)

        status_bar_height = self.metadata.status_bar_height
        nav_bar_height = self.metadata.navigation_bar_height
        header_height = 0
        footer_height = 0
        return [
            Tile(path, status_bar_height, nav_bar_height, header_height, footer_height, fullscreen)
        ]

    @staticmethod
    def _post_screenshots(name, tag, tiles, debug_url):
        response = CLIWrapper().post_screenshots(name, tag, tiles, debug_url)
        return response

    def _write_screenshot(self, png_bytes, directory):
        filepath = self._get_path(directory)
        with open(filepath, 'wb') as f:
            f.write(png_bytes)
        return filepath

    def get_debug_url(self):
        return ''

    def _get_dir(self):
        dir_path = tempfile.mkdtemp()
        return dir_path

    def _get_path(self, directory):
        suffix = '.png'
        prefix = 'percy-appium-'
        fd, filepath =  tempfile.mkstemp(suffix, prefix, directory)
        os.close(fd)
        return filepath
