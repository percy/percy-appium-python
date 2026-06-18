import os
import sys


PERCY_LOGLEVEL = os.environ.get('PERCY_LOGLEVEL')
PERCY_DEBUG = PERCY_LOGLEVEL == 'debug'
LABEL = '[\u001b[35m' + ('percy:python' if PERCY_DEBUG else 'percy') + '\u001b[39m]'

def log(message, on_debug=None, error=False):
    if isinstance(on_debug, type(None)) or (isinstance(on_debug, bool) and PERCY_DEBUG):
        output = sys.stderr if error else sys.stdout
        print(f'{LABEL} {message}', file=output)

def resolve_remote_url(command_executor):
    # Support both old and new Appium-Python-Client / Selenium versions.
    # New (Appium-Python-Client > 3 / Selenium 4.x):
    #   command_executor._client_config.remote_server_addr
    # Old: command_executor._url
    client_config = getattr(command_executor, '_client_config', None)
    if client_config:
        remote_addr = getattr(client_config, 'remote_server_addr', None)
        if remote_addr:
            return remote_addr
    return getattr(command_executor, '_url', '')
