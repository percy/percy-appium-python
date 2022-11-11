# . # pylint: disable=[arguments-differ, protected-access]
import time
import unittest
from unittest.mock import patch
from percy.lib.cache import Cache


class TestCache(unittest.TestCase):
    def setUp(self) -> None:
        self.cache = Cache
        self.session_id = 'session_id_123'
        self.prop = 'window_size'
        self.value = {'top': 'Top Value'}
        self.cache.set_cache(self.session_id, self.prop, self.value)

    def test_set_cache(self):
        with self.assertRaises(Exception) as e:
            self.cache.set_cache(123, 123, 123)
        self.assertEqual(str(e.exception), 'Argument session_id should be string')

        with self.assertRaises(Exception) as e:
            self.cache.set_cache(self.session_id, 123, 123)
        self.assertEqual(str(e.exception), 'Argument property should be string')

        self.assertIn(self.session_id, self.cache.CACHE)
        self.assertEqual(self.cache.CACHE[self.session_id][self.prop], self.value)

    def test_get_cache_invalid_args(self):
        with self.assertRaises(Exception) as e:
            self.cache.get_cache(123, 123)
        self.assertEqual(str(e.exception), 'Argument session_id should be string')

        with self.assertRaises(Exception) as e:
            self.cache.get_cache(self.session_id, 123)
        self.assertEqual(str(e.exception), 'Argument property should be string')

    @patch.object(Cache, 'cleanup_cache')
    def test_get_cache_success(self, mock_cleanup_cache):
        window_size = self.cache.get_cache(self.session_id, self.prop)
        self.assertDictEqual(window_size, self.value)
        mock_cleanup_cache.assert_called()

    @patch('percy.lib.cache.Cache.CACHE_TIMEOUT', 1)
    def test_cleanup_cache(self):
        cache_timeout = self.cache.CACHE_TIMEOUT
        time.sleep(cache_timeout + 1)
        self.assertIn(self.session_id, self.cache.CACHE)
        self.cache.cleanup_cache()
        self.assertNotIn(self.session_id, self.cache.CACHE)
