from percy.common import log
from percy.lib import AppPercy
from percy.lib.cli_wrapper import CLIWrapper


def percy_screenshot(driver, name: str, **kwargs):
    if not CLIWrapper.is_percy_enabled():
        return None
    app_percy = None
    try:
        app_percy = AppPercy(driver)
        return app_percy.screenshot(name, **kwargs)
    except Exception as e:
        log(f'Could not take screenshot "{name}"')
        if app_percy and app_percy.percy_options.ignore_errors is False:
            raise e
        log(e, on_debug=True)
        return None
