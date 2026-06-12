from functools import lru_cache
from urllib.parse import urlparse
import os
import requests

from percy.errors import CLIException
from percy.common import log
from percy.environment import Environment

DEFAULT_PERCY_CLI_API = 'http://localhost:5338'

# Hostnames that resolve to the local machine. The Percy CLI runs locally, so
# the SDK only ever needs to talk to a loopback address.
_LOOPBACK_HOSTS = frozenset({'localhost', '127.0.0.1', '::1'})


def _resolve_cli_api_address():
    # The CLI API address can be overridden via the environment. Because the SDK
    # POSTs request bodies that may carry BrowserStack credentials (capabilities)
    # to this address, an attacker-controlled value would enable SSRF and
    # credential exfiltration to an arbitrary host (CWE-306 / CWE-918). Restrict
    # it to loopback by default; allow a remote host only over HTTPS and with an
    # explicit opt-in.
    raw = os.environ.get('PERCY_CLI_API') or DEFAULT_PERCY_CLI_API
    host = (urlparse(raw).hostname or '').lower()

    if host in _LOOPBACK_HOSTS:
        return raw

    allow_remote = os.environ.get('PERCY_ALLOW_REMOTE_CLI_API', '').lower() in ('1', 'true', 'yes')
    if allow_remote and urlparse(raw).scheme == 'https':
        return raw

    log(
        f"Ignoring non-loopback PERCY_CLI_API '{raw}'; falling back to {DEFAULT_PERCY_CLI_API}. "
        "To target a remote Percy CLI, use an https:// URL and set PERCY_ALLOW_REMOTE_CLI_API=true.",
        error=True,
    )
    return DEFAULT_PERCY_CLI_API


# Maybe get the CLI API address from the environment (validated to loopback)
PERCY_CLI_API = _resolve_cli_api_address()

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
            Environment.session_type = data.get('type', None)
            version = response.headers.get('x-percy-core-version')

            if version.split('.')[0] != '1':
                log(f'Unsupported Percy CLI version, {version}', error=True)
                return False

            if int(version.split('.')[1]) < 27:
                log('Please upgrade to latest CLI version for using this SDK. Minimum compatible version is 1.27.0-beta.0', error=True)
                return False

            return True
        except Exception as e:
            log('Percy is not running, disabling screenshots', error=True)
            log(e, on_debug=True, error=True)
            return False

    def post_screenshots(self, name, tag, tiles, external_debug_url=None,
        ignored_elements_data=None, considered_elements_data=None, sync=None, test_case=None,
            th_test_case_execution_id=None,labels=None
    ):
        body = self._request_body(name, tag, tiles, external_debug_url,
            ignored_elements_data, considered_elements_data, sync, test_case, th_test_case_execution_id, labels
        )

        body['client_info'] = Environment._get_client_info()
        body['environment_info'] = Environment._get_env_info()

        response = requests.post(f'{PERCY_CLI_API}/percy/comparison', json=body, timeout=600)
        # Handle errors
        response.raise_for_status()
        data = response.json()

        if response.status_code != 200:
            raise CLIException(data.get('error', 'UnknownException'))
        return data

    def post_failed_event(self, error):
        try:
            body = {
                "clientInfo": Environment._get_client_info(True),
                "message": error,
                "errorKind": 'sdk'
            }

            response = requests.post(f'{PERCY_CLI_API}/percy/events', json=body, timeout=30)
            # Handle errors
            response.raise_for_status()
            data = response.json()

            if response.status_code != 200:
                raise CLIException(data.get('error', 'UnknownException'))
            return data
        except Exception as e:
            log(e, on_debug=True, error=True)
            return None

    def post_poa_screenshots(self, name, session_id, command_executor_url, capabilities, options=None):
        body = {
                'sessionId': session_id,
                'commandExecutorUrl': command_executor_url,
                'capabilities': dict(capabilities),
                'snapshotName': name,
                'options': options
            }

        body['client_info'] = Environment._get_client_info()
        body['environment_info'] = Environment._get_env_info()

        response = requests.post(f'{PERCY_CLI_API}/percy/automateScreenshot', json=body, timeout=600)
        # Handle errors
        response.raise_for_status()
        data = response.json()

        if response.status_code != 200:
            raise CLIException(data.get('error', 'UnknownException'))
        return data.get('data', {})

    @staticmethod
    def _request_body(name, tag, tiles, external_debug_url, ignored_elements_data,
        considered_elements_data, sync, test_case, th_test_case_execution_id, labels
    ):
        tiles = list(map(dict, tiles))
        return {
            "name": name,
            "tag": tag,
            "tiles": tiles,
            "ignored_elements_data": ignored_elements_data,
            "external_debug_url": external_debug_url,
            "considered_elements_data": considered_elements_data,
            "sync": sync,
            "test_case": test_case,
            "th_test_case_execution_id": th_test_case_execution_id,
            "labels": labels
        }
