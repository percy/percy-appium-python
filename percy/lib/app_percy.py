from appium.webdriver.webdriver import WebDriver
from percy.errors import DriverNotSupported
from percy.lib.percy_options import PercyOptions
from percy.providers.provider_resolver import ProviderResolver
from percy.metadata import MetadataResolver


class AppPercy:
    def __init__(self, driver):
        if not isinstance(driver, WebDriver):
            raise DriverNotSupported
        self.driver = driver
        self.metadata = MetadataResolver.resolve(self.driver)
        self.provider = ProviderResolver.resolve(self.driver)
        self.percy_options = PercyOptions(self.metadata.capabilities)

    def screenshot(self, name: str, fullscreen: bool = False):
        if not self.percy_options.enabled:
            return
        if not isinstance(name, str):
            raise TypeError('Argument `name` should be a string')
        if not isinstance(fullscreen, bool):
            raise TypeError('fullscreen should be boolean')
        return self.provider.screenshot(name, fullscreen)
