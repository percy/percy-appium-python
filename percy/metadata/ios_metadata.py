from percy.common import log
from percy.lib.cache import Cache
from percy.metadata.metadata import Metadata


class IOSMetadata(Metadata):
    def __init__(self, driver):
        super().__init__(driver)
        self._viewport = {}
        self._window_size = {}

    @property
    def device_screen_size(self):
        height = self.viewport.get('top') + self.viewport.get('height')
        width = self.viewport.get('width')
        if not height and not width:
            static_device_info = self.get_device_info(self.device_name)
            height = self.get_window_size().get('height') * int(static_device_info.get("scale_factor", 0))
            width = self.get_window_size().get('width') * int(static_device_info.get("scale_factor", 0))
        return {'width': width, 'height': height}

    @property
    def status_bar(self):
        height = 0
        if self.viewport.get('top'):
            height = self.viewport.get('top')
        else:
            static_device_info = self.get_device_info(self.device_name)
            scale_factor = static_device_info.get("scale_factor", 0)
            status_bar_height = static_device_info.get("status_bar", 0)
            height = int(status_bar_height) * int(scale_factor)
        return {'height': height}

    @property
    def navigation_bar(self):
        return {'height': 0}

    def get_window_size(self):
        self._window_size = Cache.get_cache(self.session_id, 'window_size')
        if not self._window_size:
            self._window_size = self.driver.get_window_size()
            Cache.set_cache(self.session_id, 'window_size', self._window_size)
        return self._window_size

    @property
    def viewport(self):
        self._viewport = Cache.get_cache(self.session_id, 'viewport')
        if self._viewport is None:
            try:
                self._viewport = self.execute_script("mobile: viewportRect")
                Cache.set_cache(self.session_id, 'viewport', self._viewport)
            except Exception:
                log("Could not use viewportRect; using static config", on_debug=True)
                # setting `viewport` as empty dict so that it's not None anymore
                Cache.set_cache(self.session_id, 'viewport', {})
        return self._viewport or {'top': 0, 'height': 0, 'width': 0}

    @property
    def device_name(self):
        if self._device_name is None:
            self._device_name = self.capabilities.get('deviceName')
        return self._device_name
