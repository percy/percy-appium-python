from abc import ABC, abstractmethod


class Metadata(ABC):
    def __init__(self, driver):
        self.driver = driver

    @property
    def capabilities(self):
        return self.driver.capabilities

    @property
    def session_id(self):
        return self.driver.session_id

    @property
    def os_name(self):
        return self.capabilities.get('platformName')

    @property
    def os_version(self):
        return self.capabilities.get('os_version')

    @property
    def remote_url(self):
        return self.driver.command_executor._url

    @property
    def orientation(self):
        return self.driver.orientation.lower()

    @property
    @abstractmethod
    def device_screen_size(self):
        raise NotImplementedError
    
    @property
    @abstractmethod
    def device_name(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def status_bar(self):
        raise NotImplementedError
    
    @property
    def status_bar_height(self):
        return self.status_bar['height']

    @property
    @abstractmethod
    def navigation_bar(self):
        raise NotImplementedError

    @property
    def navigation_bar_height(self):
        return self.navigation_bar['height']

    @property
    @abstractmethod
    def viewport(self):
        raise NotImplementedError

    def execute_script(self, command):
        return self.driver.execute_script(command)
