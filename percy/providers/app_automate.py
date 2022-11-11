import json
import os
from percy.common import log
from percy.lib.cache import Cache
from percy.providers.generic_provider import GenericProvider


class AppAutomate(GenericProvider):
    @staticmethod
    def supports(remote_url) -> bool:
        if isinstance(remote_url, str) and remote_url.rfind('browserstack') > -1:
            return True
        return False

    def screenshot(self, name: str, **kwargs):
        self.execute_percy_screenshot_begin(name)
        # Device name retrieval is custom for App Automate users
        self.metadata._device_name = kwargs.get('device_name') or self.get_device_name()
        try:
            response = super().screenshot(name, **kwargs)
            percy_screenshot_url = response.get('link', '')
            self.execute_percy_screenshot_end(name, percy_screenshot_url, 'success')
        except Exception as e:
            self.execute_percy_screenshot_end(name, percy_screenshot_url, 'failure', str(e))
            raise e

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

    def execute_percy_screenshot_begin(self, name):
        try:
            request_body = {
                'action': 'percyScreenshot',
                'arguments': {
                    'state': 'begin',
                    'percyBuildId':  os.getenv('PERCY_BUILD_ID', ''),
                    'percyBuildUrl': os.getenv('PERCY_BUILD_URL', ''),
                    'name': name
                }
            }
            command = f'browserstack_executor: {json.dumps(request_body)}'
            response = self.metadata.execute_script(command)
            response = json.loads(response)
        except Exception as e:
            log('Could not set session as Percy session')
            log('Error occurred during begin call', on_debug=True)
            log(e, on_debug=True)

    def execute_percy_screenshot_end(self, name, percy_screenshot_url, status, status_message=None):
        try:
            request_body = {
                'action': 'percyScreenshot',
                'arguments': {
                    'state': 'end',
                    'percyScreenshotUrl': percy_screenshot_url,
                    'name': name,
                    'status': status }
            }
            if status_message: request_body['arguments']['statusMessage'] = status_message
            command = f'browserstack_executor: {json.dumps(request_body)}'
            self.metadata.execute_script(command)
        except Exception as e:
            log('Error occurred during end call', on_debug=True)
            log(e, on_debug=True)
