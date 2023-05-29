import json
import os
from percy.common import log
from percy.lib.tile import Tile
from percy.providers.generic_provider import GenericProvider
from percy.environment import Environment

class AppAutomate(GenericProvider):
    @staticmethod
    def supports(remote_url) -> bool:
        if isinstance(remote_url, str):
            if remote_url.rfind("browserstack" if os.getenv("AA_DOMAIN") is None else os.getenv("AA_DOMAIN")) > -1:
                return True
        return False

    def screenshot(self, name: str, **kwargs):
        session_details = self.execute_percy_screenshot_begin(name)
        # Device name and OS version retrieval is custom for App Automate users
        if session_details is not None:
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
        build_hash = str(session_details.get("buildHash"))
        session_hash = str(session_details.get("sessionHash"))
        self.debug_url = "https://app-automate.browserstack.com/dashboard/v2/builds/" + build_hash + "/sessions/" + session_hash

    def _get_tiles(self, **kwargs):
        fullpage_ss = kwargs.get('fullpage', False)
        if not fullpage_ss:
            return super()._get_tiles(**kwargs)
        screen_lengths = kwargs.get('screen_lengths', 4)
        scrollable_xpath = kwargs.get('scollable_xpath')
        scrollable_id = kwargs.get('scrollable_id')
        data = self.execute_percy_screenshot(
            self.metadata.device_screen_size.get('height', 1),
            screen_lengths,
            scrollable_xpath,
            scrollable_id,
            self.metadata.scale_factor,
        )
        tiles = []
        status_bar_height = self.metadata.status_bar_height
        nav_bar_height = self.metadata.navigation_bar_height
        for tile_data in json.loads(data.get('result')):
            tiles.append(Tile(
                status_bar_height,
                nav_bar_height,
                tile_data.get('header_height'),
                tile_data.get('footer_height'),
                sha=tile_data.get('sha').split("-")[0]
            ))
        return tiles

    def execute_percy_screenshot_begin(self, name):
        try:
            request_body = {
                'action': 'percyScreenshot',
                'arguments': {
                    'state': 'begin',
                    'percyBuildId':  Environment.percy_build_id,
                    'percyBuildUrl': Environment.percy_build_url,
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

    def execute_percy_screenshot(self, device_height, screen_lengths, scrollable_xpath=None, scrollable_id=None, scale_factor=1):
        try:
            request_body = {
                'action': 'percyScreenshot',
                'arguments': {
                    'state': 'screenshot',
                    'percyBuildId':  Environment.percy_build_id,
                    'screenshotType': 'fullpage',
                    'scaleFactor': scale_factor,
                    'options': { 
                        "numOfTiles": screen_lengths,
                        "deviceHeight": device_height,
                        "scrollableXpath":  scrollable_xpath,
                        "scrollableId": scrollable_id
                    },
                }
            }
            command = f'browserstack_executor: {json.dumps(request_body)}'
            response = self.metadata.execute_script(command)
            response = json.loads(response)
            return response
        except Exception as e:
            log('Error occurred during screenshot call', on_debug=True)
            log(e, on_debug=True)
            raise e
