from functools import lru_cache
import os
import platform

from appium.version import version as APPIUM_VERSION
import requests
from percy.errors import CLIException

from percy.version import __version__ as SDK_VERSION
from percy.common import log


# Collect client and environment information
CLIENT_INFO = 'percy-appium-app/' + SDK_VERSION
ENV_INFO = ['appium/' + APPIUM_VERSION, 'python/' + platform.python_version()]

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

            if not data['success']: raise Exception(data['error'])
            version = response.headers.get('x-percy-core-version')

            if version.split('.')[0] != '1':
                log(f'Unsupported Percy CLI version, {version}')
                return False

            return True
        except Exception as e:
            log('Percy is not running, disabling screenshots')
            log(e, on_debug=True)
            return False

    def post_screenshots(self, name, tag, tiles, external_debug_url=None):
        body = self._request_body(name, tag, tiles, external_debug_url)

        body['client_info'] = CLIENT_INFO
        body['environment_info'] = ENV_INFO

        response = requests.post(f'{PERCY_CLI_API}/percy/comparison', json=body, timeout=30)
        # Handle errors
        response.raise_for_status()
        data = response.json()

        if response.status_code != 200:
            raise CLIException(data.get('error', 'UnknownException'))
        return data

    @staticmethod
    def _request_body(name, tag, tiles, external_debug_url):
        tiles = list(map(dict, tiles))
        return dict(name=name, tag=tag, tiles=tiles, external_debug_url=external_debug_url)
