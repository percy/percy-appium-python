import os
from appium.webdriver.webdriver import WebDriver

from percy.common import log
from percy.errors import DriverNotSupported
from percy.lib.percy_options import PercyOptions
from percy.lib.cli_wrapper import CLIWrapper

# Maybe get the CLI API address from the environment
PERCY_CLI_API = os.environ.get('PERCY_CLI_API') or 'http://localhost:5338'
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

        try:
            ignore_region_elements = [element.id for element in kwargs.get(IGNORE_ELEMENT_KEY, [])]
            kwargs.pop(IGNORE_ELEMENT_KEY, None)

            CLIWrapper().post_poa_screenshots(
                name,
                self.driver.session_id,
                self.driver.command_executor._url,
                self.driver.capabilities,
                self.driver.desired_capabilities,
                { **kwargs, "ignore_region_elements": ignore_region_elements }
            )
        except Exception as e:
            log(f'Could not take Screenshot "{name}"')
            log(f'{e}', on_debug=True)
        return None
