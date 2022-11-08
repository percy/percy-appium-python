import time


class Cache:
    CACHE = {}
    CACHE_TIMEOUT = 5 * 60  # 5 * 60 seconds
    TIMEOUT_KEY = 'last_access_time'

    def set_cache(self, session_id, property, value):
        if not isinstance(session_id, str):
            raise TypeError('Argument session_id should be string')
        if not isinstance(property, str):
            raise TypeError('Argument property should be string')
        session = self.CACHE.get(session_id, {})
        session[self.TIMEOUT_KEY] = time.time()
        session[property] = value
        self.CACHE[session_id] = session

    def get_cache(self, session_id, property):
        self.cleanup_cache()
        if not isinstance(session_id, str):
            raise TypeError('Argument session_id should be string')
        if not isinstance(property, str):
            raise TypeError('Argument property should be string')
        session = self.CACHE.get(session_id, {})
        return session.get(property, None)

    def cleanup_cache(self):
        now = time.time()
        session_ids = []
        for session_id, session in self.CACHE.items():
            timestamp = session[self.TIMEOUT_KEY]
            if now - timestamp >= self.CACHE_TIMEOUT:
                session_ids.append(session_id)
        list(map(self.CACHE.pop, session_ids))
