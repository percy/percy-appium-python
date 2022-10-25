import json
import os
import time
from appium.webdriver.webdriver import WebDriver
from percy.providers.generic_provider import GenericProvider
from percy.common import log


class AppAutomate(GenericProvider):
    SESSION_CACHE = dict()
    CACHE_PERIOD = 5 * 60  # 5 * 60 seconds

    def __init__(self, driver: WebDriver, metadata) -> None:
        super().__init__(driver, metadata)
        self._marked_percy_session = True

    @staticmethod
    def supports(remote_url) -> bool:  # resolver
        if isinstance(remote_url, str) and remote_url.rfind('browserstack') > -1:
            return True
        return False

    def screenshot(self, name: str, fullscreen: bool, debug_url: str = ''):
        self.execute_percy_screenshot_begin()
        response = super().screenshot(name, fullscreen, self.get_debug_url())
        percy_screenshot_url = response.get('link', '')
        self.execute_percy_screenshot_end(percy_screenshot_url)
        return response

    def get_debug_url(self):
        session = self._get_cached_session_id()
        if session:
            return session

        response = self.metadata.execute_script( \
            'browserstack_executor: {"action": "getSessionDetails"}')
        browser_url = json.loads(response if response else '{}').get('browser_url', '')
        self._set_session_id_cache(browser_url)
        return browser_url

    def _clean_cache(self):
        now = time.time()
        session_ids = []
        for session_id, (_, timestamp) in self.SESSION_CACHE.items():
            if now - timestamp >= self.CACHE_PERIOD:
                session_ids.append(session_id)
        list(map(self.SESSION_CACHE.pop, session_ids))

    def _get_cached_session_id(self):
        self._clean_cache()
        session_id = self.metadata.session_id
        session = self.SESSION_CACHE.get(session_id, (''))
        if session:
            self.SESSION_CACHE[session_id][1] = time.time()
            return session[0]
        return None

    def _set_session_id_cache(self, value):
        session_id = self.metadata.session_id
        self.SESSION_CACHE[session_id] = [value, time.time()]

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
        return None

    def execute_percy_screenshot_end(self, percy_screenshot_url):
        try:
            if self._marked_percy_session:
                request_body = {
                    'action': 'percyScreenshot',
                    'arguments': {'state': 'end', 'percyScreenshotUrl': percy_screenshot_url }
                }
                command = f'browserstack_executor: {json.dumps(request_body)}'
                self.metadata.execute_script(command)
        except Exception as e:
            log(e, on_debug=True)
        return None
