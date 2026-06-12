# pylint: disable=[arguments-differ, protected-access]
import copy
import unittest
from unittest.mock import patch, Mock, MagicMock, PropertyMock

from appium.webdriver.webdriver import WebDriver
from percy.errors import DriverNotSupported
from percy.lib.percy_automate import PercyOnAutomate
from percy.lib.cli_wrapper import CLIWrapper
from percy.metadata.driver_metadata import DriverMetaData
from tests.mocks.mock_methods import android_capabilities


class TestPercyOnAutomate(unittest.TestCase):
    poa_response = {'data': {'link': 'https://snapshot_url'}}

    @patch('appium.webdriver.webdriver.WebDriver')
    def setUp(self, mock_webdriver):
        mock_webdriver.__class__ = WebDriver
        self.mock_webdriver = copy.deepcopy(mock_webdriver)
        self.mock_webdriver.capabilities = copy.deepcopy(android_capabilities)

    def _disable_percy(self):
        self.mock_webdriver.capabilities['percy:options'] = {'enabled': False}
        self.mock_webdriver.capabilities['percyOptions'] = {'enabled': False}

    def test_invalid_driver(self):
        with self.assertRaises(DriverNotSupported):
            PercyOnAutomate(Mock())

    def test_screenshot_returns_none_when_disabled(self):
        self._disable_percy()
        poa = PercyOnAutomate(self.mock_webdriver)
        self.assertIsNone(poa.screenshot('screenshot 1'))

    def test_screenshot_name_not_string(self):
        poa = PercyOnAutomate(self.mock_webdriver)
        with self.assertRaises(TypeError) as cm:
            poa.screenshot(123)
        self.assertEqual(str(cm.exception), 'Argument name should be a string')

    def test_screenshot_kwargs_without_options(self):
        poa = PercyOnAutomate(self.mock_webdriver)
        with self.assertRaises(KeyError):
            poa.screenshot('screenshot 1', sync=True)

    @patch.object(DriverMetaData, 'session_id', PropertyMock(return_value='session-1'))
    @patch.object(DriverMetaData, 'command_executor_url',
                  PropertyMock(return_value='https://hub-cloud.browserstack.com/wd/hub'))
    @patch.object(DriverMetaData, 'capabilities', PropertyMock(return_value={'platformName': 'android'}))
    @patch.object(CLIWrapper, 'post_poa_screenshots', MagicMock(return_value=poa_response))
    def test_screenshot_happy_path(self):
        poa = PercyOnAutomate(self.mock_webdriver)
        result = poa.screenshot('screenshot 1', options={})
        self.assertEqual(result, self.poa_response)
        CLIWrapper.post_poa_screenshots.assert_called_once()
        # element id lists default to empty when no regions passed
        sent_options = CLIWrapper.post_poa_screenshots.call_args.args[4]
        self.assertEqual(sent_options['ignore_region_elements'], [])
        self.assertEqual(sent_options['consider_region_elements'], [])

    @patch.object(DriverMetaData, 'session_id', PropertyMock(return_value='session-1'))
    @patch.object(DriverMetaData, 'command_executor_url',
                  PropertyMock(return_value='https://hub-cloud.browserstack.com/wd/hub'))
    @patch.object(DriverMetaData, 'capabilities', PropertyMock(return_value={'platformName': 'android'}))
    @patch.object(CLIWrapper, 'post_poa_screenshots', MagicMock(return_value=poa_response))
    def test_screenshot_converts_alt_element_keys(self):
        poa = PercyOnAutomate(self.mock_webdriver)
        ignore_el = Mock()
        ignore_el.id = 'ignore-id'
        consider_el = Mock()
        consider_el.id = 'consider-id'
        options = {
            'ignoreRegionAppiumElements': [ignore_el],
            'considerRegionAppiumElements': [consider_el],
        }
        poa.screenshot('screenshot 1', options=options)
        sent_options = CLIWrapper.post_poa_screenshots.call_args.args[4]
        # alt camelCase keys are normalised, ids extracted, and raw element lists removed
        self.assertEqual(sent_options['ignore_region_elements'], ['ignore-id'])
        self.assertEqual(sent_options['consider_region_elements'], ['consider-id'])
        self.assertNotIn('ignoreRegionAppiumElements', sent_options)
        self.assertNotIn('considerRegionAppiumElements', sent_options)
        self.assertNotIn('ignore_region_appium_elements', sent_options)
        self.assertNotIn('consider_region_appium_elements', sent_options)

    @patch('percy.lib.percy_automate.log')
    @patch.object(DriverMetaData, 'session_id', PropertyMock(return_value='session-1'))
    @patch.object(DriverMetaData, 'command_executor_url',
                  PropertyMock(return_value='https://hub-cloud.browserstack.com/wd/hub'))
    @patch.object(DriverMetaData, 'capabilities', PropertyMock(return_value={'platformName': 'android'}))
    @patch.object(CLIWrapper, 'post_poa_screenshots',
                  MagicMock(side_effect=Exception('boom')))
    def test_screenshot_swallows_exception_and_returns_none(self, mock_log):
        poa = PercyOnAutomate(self.mock_webdriver)
        self.assertIsNone(poa.screenshot('screenshot 1', options={}))
        mock_log.assert_called()


if __name__ == '__main__':
    unittest.main()
