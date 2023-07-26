from functools import lru_cache
import os
import requests

from percy.errors import CLIException
from percy.common import log
from percy.environment import Environment

# Maybe get the CLI API address from the environment
PERCY_CLI_API = os.environ.get('PERCY_CLI_API') or 'http://localhost:5338'

class CLIWrapper:
    def __init__(self) -> None:
        pass

    # Check if Percy is enabled, caching the result so it is only checked once
    @staticmethod
    @lru_cache(maxsize=None)
    def is_percy_enabled():
        try:
            response = requests.get(f'{PERCY_CLI_API}/percy/healthcheck', timeout=10)
            response.raise_for_status()
            data = response.json()

            if not data['success']: raise CLIException(data['error'])
            Environment.percy_build_id = data['build']['id']
            Environment.percy_build_url = data['build']['url']
            Environment.session_type = data['type']
            version = response.headers.get('x-percy-core-version')

            if version.split('.')[0] != '1':
                log(f'Unsupported Percy CLI version, {version}')
                return False

            return True
        except Exception as e:
            log('Percy is not running, disabling screenshots')
            log(e, on_debug=True)
            return False

    def post_screenshots(self, name, tag, tiles, external_debug_url=None, ignored_elements_data=None, considered_elements_data=None):
        body = self._request_body(name, tag, tiles, external_debug_url, ignored_elements_data, considered_elements_data)

        body['client_info'] = Environment._get_client_info()
        body['environment_info'] = Environment._get_env_info()

        response = requests.post(f'{PERCY_CLI_API}/percy/comparison', json=body, timeout=30)
        # Handle errors
        response.raise_for_status()
        data = response.json()

        if response.status_code != 200:
            raise CLIException(data.get('error', 'UnknownException'))
        return data

    def post_poa_screenshots(self, name, session_id, command_executor_url, capabilities, desired_capabilities, options=None):
        body = {
                'sessionId': session_id,
                'commandExecutorUrl': command_executor_url,
                'capabilities': dict(capabilities),
                'sessionCapabilites':dict(desired_capabilities),
                'snapshotName': name,
                'options': options
            }

        body['client_info'] = Environment._get_client_info()
        body['environment_info'] = Environment._get_env_info()

        response = requests.post(f'{PERCY_CLI_API}/percy/automateScreenshot', json=body, timeout=30)
        # Handle errors
        response.raise_for_status()
        data = response.json()

        if response.status_code != 200:
            raise CLIException(data.get('error', 'UnknownException'))
        return data

    @staticmethod
    def _request_body(name, tag, tiles, external_debug_url, ignored_elements_data, considered_elements_data):
        tiles = list(map(dict, tiles))
        return {
            "name": name,
            "tag": tag,
            "tiles": tiles,
            "ignored_elements_data": ignored_elements_data,
            "external_debug_url": external_debug_url,
            "considered_elements_data": considered_elements_data 
        }
