import os
import re
import sys


PERCY_LOGLEVEL = os.environ.get('PERCY_LOGLEVEL')
PERCY_DEBUG = PERCY_LOGLEVEL == 'debug'
LABEL = '[\u001b[35m' + ('percy:python' if PERCY_DEBUG else 'percy') + '\u001b[39m]'

# Terminal escape sequences (CSI / OSC / other ESC-prefixed) and C0/C1 control
# characters other than newline and tab. Messages can carry text from remote
# sources (driver capabilities, server errors), so these are stripped to keep
# them from rewriting or forging terminal / CI log output.
_UNSAFE_LOG_CHARS = re.compile(
    r'\x1b\[[0-?]*[ -/]*[@-~]'                # CSI sequences, e.g. colors, cursor moves
    r'|\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)?'   # OSC sequences, e.g. window title, hyperlinks
    r'|\x1b[ -/]*[0-~]?'                      # any other ESC sequence, or a lone ESC
    r'|[\x00-\x08\x0b-\x1f\x7f-\x9f]'          # remaining control chars (keeps \t and \n)
)

def _sanitize(message):
    # Continuation lines are indented so a multi-line message can't start a
    # line that looks like separate SDK output.
    return _UNSAFE_LOG_CHARS.sub('', str(message)).replace('\n', '\n  ')

def log(message, on_debug=None, error=False):
    if isinstance(on_debug, type(None)) or (isinstance(on_debug, bool) and PERCY_DEBUG):
        output = sys.stderr if error else sys.stdout
        print(f'{LABEL} {_sanitize(message)}', file=output)

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
