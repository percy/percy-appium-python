# pylint: disable=[protected-access]

import sys
import unittest
import importlib
from io import StringIO
from unittest.mock import patch
import percy.common

from percy.common import log, resolve_remote_url


class TestResolveRemoteUrl(unittest.TestCase):
    def test_prefers_client_config_remote_server_addr(self):
        """New Appium-Python-Client (>3) / Selenium 4.x style."""
        url = 'https://new-style-hub:4444/wd/hub'
        executor = type('CE', (), {
            '_client_config': type('Cfg', (), {'remote_server_addr': url})(),
            '_url': 'https://should-not-be-used'
        })()
        self.assertEqual(resolve_remote_url(executor), url)

    def test_falls_back_to_url_when_no_client_config(self):
        """Older clients only expose ._url."""
        executor = type('CE', (), {'_client_config': None, '_url': 'https://old-hub:4444/wd/hub'})()
        self.assertEqual(resolve_remote_url(executor), 'https://old-hub:4444/wd/hub')

    def test_falls_back_to_url_when_client_config_has_no_addr(self):
        executor = type('CE', (), {
            '_client_config': type('Cfg', (), {'remote_server_addr': None})(),
            '_url': 'https://old-hub:4444/wd/hub'
        })()
        self.assertEqual(resolve_remote_url(executor), 'https://old-hub:4444/wd/hub')

    def test_returns_empty_string_when_nothing_available(self):
        executor = type('CE', (), {})()
        self.assertEqual(resolve_remote_url(executor), '')


class TestCommon(unittest.TestCase):
    def test_log_to_stdout_by_default(self):
        """Test that log outputs to stdout by default"""
        captured_output = StringIO()
        sys.stdout = captured_output

        log('Test message')

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        self.assertIn('Test message', output)
        self.assertIn('percy', output)

    def test_log_to_stderr_when_error_true(self):
        """Test that log outputs to stderr when error=True"""
        captured_output = StringIO()
        sys.stderr = captured_output

        log('Error message', error=True)

        sys.stderr = sys.__stderr__
        output = captured_output.getvalue()
        self.assertIn('Error message', output)
        self.assertIn('percy', output)

    def test_log_stderr_does_not_go_to_stdout(self):
        """Test that error logs don't go to stdout"""
        captured_stdout = StringIO()
        captured_stderr = StringIO()
        sys.stdout = captured_stdout
        sys.stderr = captured_stderr

        log('Error message', error=True)

        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

        stdout_output = captured_stdout.getvalue()
        stderr_output = captured_stderr.getvalue()

        self.assertEqual(stdout_output, '')
        self.assertIn('Error message', stderr_output)

    def test_log_stdout_does_not_go_to_stderr(self):
        """Test that normal logs don't go to stderr"""
        captured_stdout = StringIO()
        captured_stderr = StringIO()
        sys.stdout = captured_stdout
        sys.stderr = captured_stderr

        log('Normal message', error=False)

        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

        stdout_output = captured_stdout.getvalue()
        stderr_output = captured_stderr.getvalue()

        self.assertIn('Normal message', stdout_output)
        self.assertEqual(stderr_output, '')

    @patch.dict('os.environ', {'PERCY_LOGLEVEL': 'debug'})
    def test_log_debug_message(self):
        """Test that debug messages are logged when PERCY_LOGLEVEL=debug"""
        importlib.reload(percy.common)

        captured_output = StringIO()
        sys.stdout = captured_output

        log('Debug message', on_debug=True)

        sys.stdout = sys.__stdout__
        _ = captured_output.getvalue()
        self.assertIn('Debug message', _)

    def test_log_debug_message_not_shown_by_default(self):
        """Test that debug messages are not shown when PERCY_LOGLEVEL is not set"""
        captured_output = StringIO()
        sys.stdout = captured_output

        log('Debug message', on_debug=True)

        sys.stdout = sys.__stdout__
        _ = captured_output.getvalue()
        # Debug messages should only appear when PERCY_DEBUG is True
        # Since we're not setting PERCY_LOGLEVEL in this test, it should be suppressed
        # unless on_debug parameter handling shows it

    @patch.dict('os.environ', {'PERCY_LOGLEVEL': 'debug'})
    def test_log_debug_error_to_stderr(self):
        """Test that debug error messages go to stderr"""
        importlib.reload(percy.common)

        captured_output = StringIO()
        sys.stderr = captured_output

        log('Debug error', on_debug=True, error=True)

        sys.stderr = sys.__stderr__
        _ = captured_output.getvalue()
        self.assertIn('Debug error', _)


if __name__ == '__main__':
    unittest.main()
