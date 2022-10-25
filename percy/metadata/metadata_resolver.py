from percy.errors import PlatformNotSupported
from percy.metadata.android_metadata import AndroidMetadata
from percy.metadata.ios_metadata import IOSMetadata


class MetadataResolver:
    @staticmethod
    def resolve(driver):
        if driver.capabilities.get('platformName', '').lower() == 'android':
            return AndroidMetadata(driver)
        elif driver.capabilities.get('platformName', '').lower() == 'ios':
            return IOSMetadata(driver)
        else:
            raise PlatformNotSupported
