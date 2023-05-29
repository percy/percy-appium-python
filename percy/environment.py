import platform

from appium.version import version as APPIUM_VERSION
from percy.version import __version__ as SDK_VERSION

class Environment:
    percy_build_id = None
    percy_build_url = None

    @staticmethod
    def _get_client_info():
        return 'percy-appium-app/' + SDK_VERSION

    @staticmethod
    def _get_env_info():
        return ['appium/' + APPIUM_VERSION, 'python/' + platform.python_version()]
