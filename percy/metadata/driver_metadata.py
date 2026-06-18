from percy.lib.cache import Cache

class DriverMetaData:
    def __init__(self, driver):
        self.driver = driver

    @property
    def session_id(self):
        return self.driver.session_id

    @property
    def command_executor_url(self):
        url = Cache.get_cache(self.session_id, Cache.command_executor_url)
        if url is None:
            url = self._extract_remote_url()
            Cache.set_cache(self.session_id, Cache.command_executor_url, url)
            return url
        return url

    def _extract_remote_url(self):
        # Support both old and new Appium-Python-Client / Selenium versions.
        # New (Appium-Python-Client > 3 / Selenium 4.x):
        #   driver.command_executor._client_config.remote_server_addr
        # Old: driver.command_executor._url
        command_executor = self.driver.command_executor
        client_config = getattr(command_executor, '_client_config', None)
        if client_config:
            remote_addr = getattr(client_config, 'remote_server_addr', None)
            if remote_addr:
                return remote_addr
        return getattr(command_executor, '_url', '') # pylint: disable=W0212

    @property
    def capabilities(self):
        caps = Cache.get_cache(self.session_id, Cache.capabilities)
        if caps is None:
            caps = dict(self.driver.capabilities)
            Cache.set_cache(self.session_id, Cache.capabilities, caps)
            return caps
        return caps
