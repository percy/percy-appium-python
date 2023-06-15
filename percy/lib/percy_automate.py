import os, requests
from percy.common import log
from appium.webdriver.webdriver import WebDriver
from percy.errors import DriverNotSupported
from percy.lib.percy_options import PercyOptions
from percy.environment import Environment

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

            # Post to automateScreenshot endpoint with driver options and other info
            response = requests.post(f'{PERCY_CLI_API}/percy/automateScreenshot', json={
                'client_info': Environment._get_client_info(),
                'environment_info': Environment._get_env_info(),
                'sessionId': self.driver.session_id,
                'commandExecutorUrl': self.driver.command_executor._url, # pylint: disable=W0212
                'capabilities': dict(self.driver.capabilities),
                'sessionCapabilites':dict(self.driver.desired_capabilities),
                'snapshotName': name,
                'options': { **kwargs, "ignore_region_elements": ignore_region_elements }
            }, timeout=30)

            # Handle errors
            response.raise_for_status()
            data = response.json()
            if not data['success']: raise Exception(data['error'])
        except Exception as e:
            log(f'Could not take Screenshot "{name}"')
            log(f'{e}')
