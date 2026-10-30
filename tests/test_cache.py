# . # pylint: disable=[arguments-differ, protected-access]
import itertools
import os
import subprocess
import sys
import textwrap
import threading
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

    def test_concurrent_set_during_cleanup_is_serialized(self):
        errors = []
        started = threading.Event()

        class MidIterationDict(dict):
            def items(inner):  # pylint: disable=no-self-argument
                it = iter(dict.items(inner))
                yield from itertools.islice(it, 1)
                # a writer starting now mutates the dict mid-iteration unless locked
                writer.start()
                started.wait(2)
                writer.join(0.2)
                yield from it

        def run_writer():
            started.set()
            try:
                self.cache.set_cache('other_session', 'k', 'v')
            except Exception as e:  # pylint: disable=broad-except
                errors.append(e)

        writer = threading.Thread(target=run_writer)
        data = MidIterationDict()
        data['seed'] = {self.cache.TIMEOUT_KEY: time.time()}
        with patch('percy.lib.cache.Cache.CACHE', data):
            self.cache.cleanup_cache()
            writer.join(2)
            self.assertFalse(writer.is_alive())
            self.assertEqual(errors, [])
            self.assertIn('seed', data)
            self.assertIn('other_session', data)

    def test_get_cache_does_not_deadlock(self):
        # child process so a regression to a non-reentrant lock can't hang this run
        script = textwrap.dedent("""
            from percy.lib.cache import Cache
            Cache.set_cache('s', 'p', 'v')
            assert Cache.get_cache('s', 'p') == 'v'
        """)
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with subprocess.Popen([sys.executable, '-c', script], cwd=root,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              universal_newlines=True) as process:
            try:
                _, stderr = process.communicate(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate()
                self.fail('get_cache did not complete before the timeout')
        self.assertEqual(process.returncode, 0, stderr)
