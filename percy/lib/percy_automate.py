from appium.webdriver.webdriver import WebDriver

from percy.common import log
from percy.errors import DriverNotSupported
from percy.lib.percy_options import PercyOptions
from percy.lib.cli_wrapper import CLIWrapper

IGNORE_ELEMENT_KEY = 'ignore_region_appium_elements'

class PercyOnAutomate:
    def __init__(self, driver):
        if not isinstance(driver, WebDriver):
            raise DriverNotSupported
        self.driver = driver
        self.percy_options = PercyOptions(self.driver.capabilities)

    def screenshot(self, name: str, **kwargs):
        if not self.percy_options.enabled:
            return None
        if not isinstance(name, str):
            raise TypeError('Argument name should be a string')
        if kwargs and 'options' not in kwargs:
            raise KeyError('Please pass last parameter as "options" = ...')
        options = kwargs['options'] if 'options' in kwargs else {}

        try:
            ignore_region_elements = [element.id for element in options.get(IGNORE_ELEMENT_KEY, [])]
            options.pop(IGNORE_ELEMENT_KEY, None)

            CLIWrapper().post_poa_screenshots(
                name,
                self.driver.session_id,
                self.driver.command_executor._url,
                self.driver.capabilities,
                self.driver.desired_capabilities,
                { **options, "ignore_region_elements": ignore_region_elements }
            )
        except Exception as e:
            log(f'Could not take Screenshot "{name}"')
            log(f'{e}', on_debug=True)
        return None
