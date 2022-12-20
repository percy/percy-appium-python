import json
import os
from percy.common import log
from percy.providers.generic_provider import GenericProvider


class AppAutomate(GenericProvider):
    @staticmethod
    def supports(remote_url) -> bool:
        if isinstance(remote_url, str) and remote_url.rfind('browserstack') > -1:
            return True
        return False

    def screenshot(self, name: str, **kwargs):
        session_details = self.execute_percy_screenshot_begin(name)
        # Device name and OS version retrieval is custom for App Automate users
        self.metadata._device_name = kwargs.get('device_name') or session_details.get("deviceName")
        self.metadata._os_version = session_details.get("osVersion")
        self.set_debug_url(session_details)
        try:
            response = super().screenshot(name, **kwargs)
            percy_screenshot_url = response.get('link', '')
            self.execute_percy_screenshot_end(name, percy_screenshot_url, 'success')
        except Exception as e:
            self.execute_percy_screenshot_end(name, percy_screenshot_url, 'failure', str(e))
            raise e

    def set_debug_url(self, session_details):
        build_hash = session_details.get("buildHash")
        session_hash = session_details.get("sessionHash")
        self.debug_url = "https://app-automate.browserstack.com/dashboard/v2/builds/" + build_hash + "/sessions/" + session_hash

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
            return response
        except Exception as e:
            log('Could not set session as Percy session')
            log('Error occurred during begin call', on_debug=True)
            log(e, on_debug=True)
            return None

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
