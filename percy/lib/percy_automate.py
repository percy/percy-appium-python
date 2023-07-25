from appium.webdriver.webdriver import WebDriver

from percy.common import log
from percy.errors import DriverNotSupported
from percy.lib.percy_options import PercyOptions
from percy.lib.cli_wrapper import CLIWrapper

IGNORE_ELEMENT_KEY = 'ignore_region_appium_elements'
IGNORE_ELEMENT_ALT_KEY = 'ignoreRegionAppiumElements'
CONSIDER_ELEMENT_KEY = 'consider_region_appium_elements'
CONSIDER_ELEMENT_ALT_KEY = 'considerRegionAppiumElements'

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
            if IGNORE_ELEMENT_ALT_KEY in options:
                options[IGNORE_ELEMENT_KEY] = options[IGNORE_ELEMENT_ALT_KEY]
                options.pop(IGNORE_ELEMENT_ALT_KEY)
            if CONSIDER_ELEMENT_ALT_KEY in options:
                options[CONSIDER_ELEMENT_KEY] = options[CONSIDER_ELEMENT_ALT_KEY]
                options.pop(CONSIDER_ELEMENT_ALT_KEY)

            ignore_region_elements = [element.id for element in options.get(IGNORE_ELEMENT_KEY, [])]
            consider_region_elements = [element.id for element in options.get(CONSIDER_ELEMENT_KEY, [])]
            options.pop(IGNORE_ELEMENT_KEY, None)
            options.pop(CONSIDER_ELEMENT_KEY, None)

            CLIWrapper().post_poa_screenshots(
                name,
                self.driver.session_id,
                self.driver.command_executor._url,
                self.driver.capabilities,
                self.driver.desired_capabilities,
                { **options, "ignore_region_elements": ignore_region_elements, "consider_region_elements" : consider_region_elements }
            )
        except Exception as e:
            log(f'Could not take Screenshot "{name}"')
            log(f'{e}', on_debug=True)
        return None
