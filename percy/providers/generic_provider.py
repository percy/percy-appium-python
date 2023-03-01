import os
import tempfile
from pathlib import Path

from appium.webdriver.webdriver import WebDriver

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

        return self._post_screenshots(name, tag, tiles, self.get_debug_url())

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
