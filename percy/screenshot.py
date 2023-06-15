from percy.common import log
from percy.lib import AppPercy, PercyOnAutomate
from percy.lib.cli_wrapper import CLIWrapper


def percy_screenshot(driver, name: str, **kwargs):
    try:
        cli_status = CLIWrapper.is_percy_enabled()
        if not cli_status:
            return None
        
        ProviderClass = PercyOnAutomate if cli_status == 'automate' else AppPercy
        app_percy = None
        app_percy = ProviderClass(driver)
        return app_percy.screenshot(name, **kwargs)
    except Exception as e:
        log(f'Could not take screenshot "{name}"')
        if app_percy and app_percy.percy_options.ignore_errors is False:
            raise e
        log(e, on_debug=True)
        return None
