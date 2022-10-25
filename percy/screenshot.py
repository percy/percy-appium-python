from appium.webdriver.webdriver import WebDriver

from percy.common import log
from percy.lib import AppPercy
from percy.lib.cli_wrapper import CLIWrapper


def percy_screenshot(driver: WebDriver, name: str, fullscreen: bool=False):
    if not CLIWrapper.is_percy_enabled():
        return
    try:
        app_percy = AppPercy(driver)
        return app_percy.screenshot(name, fullscreen)
    except Exception as e:
        log(f'Could not take screenshot "{name}"')
        log(e, on_debug=True)
        if not app_percy.percy_options.ignore_errors:
            raise e
