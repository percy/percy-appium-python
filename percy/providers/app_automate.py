import json
import os
from appium.webdriver.webdriver import WebDriver
from percy.common import log
from percy.lib.cache import Cache
from percy.providers.generic_provider import GenericProvider


class AppAutomate(GenericProvider):
    def __init__(self, driver: WebDriver, metadata) -> None:
        super().__init__(driver, metadata)
        self._marked_percy_session = True

    @staticmethod
    def supports(remote_url) -> bool:
        if isinstance(remote_url, str) and remote_url.rfind('browserstack') > -1:
            return True
        return False

    def screenshot(self, name: str, **kwargs):
        self.execute_percy_screenshot_begin()
        # Device name retrieval is custom for App Automate users
        self.metadata._device_name = kwargs.get('device_name') or self.get_device_name()
        response = super().screenshot(name, **kwargs)
        percy_screenshot_url = response.get('link', '')
        self.execute_percy_screenshot_end(percy_screenshot_url)
        return response

    def get_session_details(self):
        session_details = Cache.get_cache(self.metadata.session_id, 'session_details')
        if session_details: return session_details
        response = {}
        try:
            response = self.metadata.execute_script(
                'browserstack_executor: {"action": "getSessionDetails"}')
            response = json.loads(response if response else '{}')
            Cache.set_cache(self.metadata.session_id, 'session_details', response)
        except Exception as e:
            log('Could not get session details from AppAutomate')
            log(e, on_debug=True)
        return response

    def get_debug_url(self):
        browser_url = self.get_session_details().get('browser_url', '')
        return browser_url

    def get_device_name(self):
        return self.get_session_details().get('device', '')

    def execute_percy_screenshot_begin(self):
        try:
            request_body = {
                'action': 'percyScreenshot',
                'arguments': {
                    'state': 'begin',
                    'percyBuildId':  os.getenv('PERCY_BUILD_ID', ''),
                    'percyBuildUrl': os.getenv('PERCY_BUILD_URL', '')
                }
            }
            command = f'browserstack_executor: {json.dumps(request_body)}'
            response = self.metadata.execute_script(command)
            response = json.loads(response)
            self._marked_percy_session = response.get("success") is True
        except Exception as e:
            log('Could not set session as Percy session')
            log(e, on_debug=True)
            self._marked_percy_session = False

    def execute_percy_screenshot_end(self, percy_screenshot_url):
        try:
            if self._marked_percy_session:
                request_body = {
                    'action': 'percyScreenshot',
                    'arguments': {
                        'state': 'end',
                        'percyScreenshotUrl': percy_screenshot_url }
                }
                command = f'browserstack_executor: {json.dumps(request_body)}'
                self.metadata.execute_script(command)
        except Exception as e:
            log(e, on_debug=True)
