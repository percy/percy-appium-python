from percy.metadata.metadata import Metadata


class AndroidMetadata(Metadata):
    def __init__(self, driver):
        super().__init__(driver)
        self._bars = None

    @property
    def device_screen_size(self):
        width, height = self.capabilities['deviceScreenSize'].split('x')
        return {'width': int(width), 'height': int(height)}

    def get_system_bars(self):
        if not self._bars:
            self._bars = self.driver.get_system_bars()
        return self._bars

    @property
    def status_bar(self):
        return self.get_system_bars().get('statusBar')

    @property
    def navigation_bar(self):
        return self.get_system_bars().get('navigationBar')

    @property
    def viewport(self):
        return self.capabilities.get('viewportRect', {})

    @property
    def device_name(self):
        if self._device_name is None:
            desired_caps = self.capabilities.get('desired', {})
            _device_name = desired_caps.get('deviceName')
            _device = desired_caps.get('device')
            _device_name = _device_name or _device
            _device_model = self.capabilities.get('deviceModel')
            self._device_name = _device_name or _device_model
        return self._device_name
