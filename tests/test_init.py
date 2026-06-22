# pylint: disable=[protected-access]
import importlib
import sys
import unittest
from unittest.mock import patch, Mock

import percy


class TestPercyInitFallbacks(unittest.TestCase):
    """The package exposes percy_snapshot/percy_screenshot with defensive
    fallbacks that raise a helpful error when the companion package that
    actually implements the command is not installed."""

    def test_percy_snapshot_fallback_raises_when_selenium_missing(self):
        # percy-appium-app does not ship percy.snapshot, so percy_snapshot is
        # the fallback and must point users at the percy-selenium package.
        with self.assertRaises(ModuleNotFoundError) as cm:
            percy.percy_snapshot(driver=Mock())
        self.assertIn('percy-selenium', str(cm.exception))

    def test_percySnapshot_delegates_to_percy_snapshot(self):
        with patch('percy.percy_snapshot') as mock_snapshot:
            mock_snapshot.return_value = 'delegated'
            result = percy.percySnapshot(browser='driver', name='snap')
            self.assertEqual(result, 'delegated')
            mock_snapshot.assert_called_once_with(driver='driver', name='snap')

    def test_percy_screenshot_fallback_raises_when_appium_missing(self):
        # Force the percy.screenshot import to fail and reload the package so
        # the defensive percy_screenshot fallback is exercised, then restore.
        with patch.dict(sys.modules, {'percy.screenshot': None}):
            importlib.reload(percy)
            try:
                with self.assertRaises(ModuleNotFoundError) as cm:
                    percy.percy_screenshot(driver=Mock())
                self.assertIn('percy-appium-app', str(cm.exception))
            finally:
                importlib.reload(percy)


if __name__ == '__main__':
    unittest.main()
