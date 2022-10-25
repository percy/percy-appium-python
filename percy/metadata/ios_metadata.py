from percy.metadata.metadata import Metadata


class IOSMetadata(Metadata):
    def __init__(self, driver):
        super().__init__(driver)
        self._viewport = None

    @property
    def device_screen_size(self):
        height = self.viewport.get('top') + self.viewport.get('height')
        width = self.viewport.get('width')
        return {'width': width, 'height': height}

    @property
    def status_bar(self):
        return {'height': self.viewport.get('top')}

    @property
    def navigation_bar(self):
        return {'height': 0}

    def get_viewport(self):
        if not self._viewport:
            self._viewport = self.execute_script("mobile: viewportRect")
        return self._viewport

    @property
    def viewport(self):
        return self.get_viewport()

    @property
    def device_name(self):
        return self.capabilities.get('deviceName')
