import os
import sys


PERCY_LOGLEVEL = os.environ.get('PERCY_LOGLEVEL')
PERCY_DEBUG = PERCY_LOGLEVEL == 'debug'
LABEL = '[\u001b[35m' + ('percy:python' if PERCY_DEBUG else 'percy') + '\u001b[39m]'

def log(message, on_debug=None, error=False):
    if isinstance(on_debug, type(None)) or (isinstance(on_debug, bool) and PERCY_DEBUG):
        output = sys.stderr if error else sys.stdout
        print(f'{LABEL} {message}', file=output)
