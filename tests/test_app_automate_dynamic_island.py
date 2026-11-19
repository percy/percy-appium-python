# pylint: disable=[arguments-differ, protected-access]
import json
import unittest
from unittest.mock import MagicMock, patch, PropertyMock
from appium.webdriver.webdriver import WebDriver
from percy.providers.app_automate import AppAutomate
from percy.providers.generic_provider import GenericProvider
from percy.metadata import AndroidMetadata
from percy.environment import Environment
from tests.mocks.mock_methods import android_capabilities

ISLAND_FIELDS = {
    'dynamic_island_rect': {'x': 157.33, 'y': 14, 'width': 125.33, 'height': 36.67},
    'screen_size_points': {'width': 440, 'height': 956},
    'device_orientation': 'UIA_DEVICE_ORIENTATION_LANDSCAPERIGHT'
}
PLAIN_TILE = {'sha': 'sha-25568755', 'header_height': 0, 'footer_height': 0}
ISLAND_TILE = {**PLAIN_TILE, **ISLAND_FIELDS}


def patch_android_metadata(test):
    for name, value in (('device_screen_size', {'width': 1080, 'height': 1920}),
                        ('navigation_bar_height', 150), ('status_bar_height', 100)):
        test = patch.object(AndroidMetadata, name, PropertyMock(return_value=value))(test)
    return test


def mock_tiles_result(*tiles):
    return MagicMock(return_value={'result': json.dumps(list(tiles))})


class TestAppAutomateDynamicIsland(unittest.TestCase):
    @patch('appium.webdriver.webdriver.WebDriver')
    def setUp(self, mock_webdriver) -> None:
        # metadata dimensions are patched per test with @patch_android_metadata
        mock_webdriver.__class__ = WebDriver
        mock_webdriver.capabilities = android_capabilities
        self.app_automate = AppAutomate(mock_webdriver, AndroidMetadata(mock_webdriver))

    @patch_android_metadata
    def test_get_tiles_reads_dynamic_island_fields_from_first_tile(self):
        self.app_automate.execute_percy_screenshot = mock_tiles_result(ISLAND_TILE)
        self.app_automate._get_tiles()
        self.assertDictEqual(self.app_automate._comparison_extras(dynamic_island=True), {
            'dynamic_island': True, **ISLAND_FIELDS
        })

    @patch_android_metadata
    def test_comparison_extras_sends_geometry_when_dynamic_island_unset(self):
        # geometry is still sent so the .percy.yml default can apply
        self.app_automate.execute_percy_screenshot = mock_tiles_result(ISLAND_TILE)
        self.app_automate._get_tiles()
        self.assertDictEqual(self.app_automate._comparison_extras(), ISLAND_FIELDS)

    @patch_android_metadata
    def test_comparison_extras_drops_geometry_when_dynamic_island_false(self):
        self.app_automate.execute_percy_screenshot = mock_tiles_result(ISLAND_TILE)
        self.app_automate._get_tiles()
        self.assertDictEqual(self.app_automate._comparison_extras(dynamic_island=False), {'dynamic_island': False})

    @patch_android_metadata
    def test_get_tiles_without_dynamic_island_fields(self):
        self.app_automate.execute_percy_screenshot = mock_tiles_result(PLAIN_TILE)
        tiles = self.app_automate._get_tiles()
        self.assertEqual(len(tiles), 1)
        self.assertDictEqual(self.app_automate._comparison_extras(), {})
        self.assertDictEqual(self.app_automate._comparison_extras(dynamic_island=True), {'dynamic_island': True})

    @patch_android_metadata
    def test_get_tiles_drops_malformed_dynamic_island_fields(self):
        tile = {**PLAIN_TILE, 'dynamic_island_rect': 'bad', 'screen_size_points': None,
                'device_orientation': 'PORTRAIT'}
        self.app_automate.execute_percy_screenshot = mock_tiles_result(tile)
        self.app_automate._get_tiles()
        self.assertDictEqual(self.app_automate._comparison_extras(), {'device_orientation': 'PORTRAIT'})

    @patch('percy.providers.app_automate.log')
    def test_extract_dynamic_island_fields_swallows_errors(self, mock_log):
        # a tile that is not a mapping must not fail the screenshot
        self.assertDictEqual(AppAutomate._extract_dynamic_island_fields(['not', 'a', 'dict']), {})
        mock_log.assert_any_call('Could not read dynamic island data', on_debug=True, error=True)
        self.assertEqual(mock_log.call_count, 2)

    @patch_android_metadata
    def test_get_tiles_skips_dynamic_island_for_fullpage(self):
        self.app_automate.execute_percy_screenshot = mock_tiles_result(ISLAND_TILE, ISLAND_TILE)
        tiles = self.app_automate._get_tiles(fullpage=True)
        self.assertEqual(len(tiles), 2)
        self.assertDictEqual(self.app_automate._comparison_extras(dynamic_island=True), {'dynamic_island': True})

    @patch_android_metadata
    def test_get_tiles_resets_dynamic_island_fields_between_screenshots(self):
        self.app_automate.execute_percy_screenshot = mock_tiles_result(ISLAND_TILE)
        self.app_automate._get_tiles()
        self.app_automate.execute_percy_screenshot = mock_tiles_result(PLAIN_TILE)
        self.app_automate._get_tiles()
        self.assertDictEqual(self.app_automate._comparison_extras(), {})

    @patch_android_metadata
    @patch.object(GenericProvider, '_post_screenshots', return_value={'link': 'snapshot-url', 'data': {}})
    @patch.object(GenericProvider, '_get_tag', MagicMock(return_value={'name': 'iPhone'}))
    @patch.object(GenericProvider, '_find_regions', MagicMock(return_value=[]))
    @patch.object(AppAutomate, 'execute_percy_screenshot_begin', MagicMock(return_value=None))
    @patch.object(AppAutomate, 'execute_percy_screenshot_end', MagicMock())
    def test_screenshot_posts_dynamic_island_extras(self, mock_post_screenshots):
        self.app_automate.execute_percy_screenshot = mock_tiles_result(ISLAND_TILE)
        self.app_automate.screenshot('Screenshot 1', dynamic_island=True)
        extras = mock_post_screenshots.call_args.args[-1]
        self.assertDictEqual(extras, {'dynamic_island': True, **ISLAND_FIELDS})

    @patch_android_metadata
    @patch.object(GenericProvider, '_post_screenshots', return_value={'link': 'snapshot-url', 'data': {}})
    @patch.object(GenericProvider, '_get_tag', MagicMock(return_value={'name': 'Pixel'}))
    @patch.object(GenericProvider, '_find_regions', MagicMock(return_value=[]))
    @patch.object(AppAutomate, 'execute_percy_screenshot_begin', MagicMock(return_value=None))
    @patch.object(AppAutomate, 'execute_percy_screenshot_end', MagicMock())
    def test_screenshot_posts_no_extras_by_default(self, mock_post_screenshots):
        self.app_automate.execute_percy_screenshot = mock_tiles_result(PLAIN_TILE)
        self.app_automate.screenshot('Screenshot 1')
        self.assertDictEqual(mock_post_screenshots.call_args.args[-1], {})


class TestAppAutomateDynamicIslandRequest(unittest.TestCase):
    """Whether the screenshot request asks App Automate for the island geometry."""

    @patch('appium.webdriver.webdriver.WebDriver')
    def setUp(self, mock_webdriver) -> None:
        mock_webdriver.__class__ = WebDriver
        mock_webdriver.capabilities = android_capabilities
        self.app_automate = AppAutomate(mock_webdriver, AndroidMetadata(mock_webdriver))
        Environment.percy_config = None

    def tearDown(self) -> None:
        Environment.percy_config = None

    def requested(self, **kwargs):
        mock_screenshot = mock_tiles_result(PLAIN_TILE)
        self.app_automate.execute_percy_screenshot = mock_screenshot
        self.app_automate._get_tiles(**kwargs)
        return mock_screenshot.call_args.kwargs['dynamic_island']

    def sent_options(self, **kwargs):
        with patch.object(AndroidMetadata, 'execute_script', return_value='{"result": "[]"}') as mock_execute:
            self.app_automate.execute_percy_screenshot(1080, 'singlepage', 5, **kwargs)
        command = mock_execute.call_args.args[0]
        return json.loads(command.split('browserstack_executor: ', 1)[1])['arguments']['options']

    @patch_android_metadata
    def test_requested_when_screenshot_opts_in(self):
        self.assertTrue(self.requested(dynamic_island=True))

    @patch_android_metadata
    def test_not_requested_by_default(self):
        self.assertFalse(self.requested())

    @patch_android_metadata
    def test_requested_from_config_default(self):
        Environment.percy_config = {'snapshot': {'dynamicIsland': True}}
        self.assertTrue(self.requested())

    @patch_android_metadata
    def test_screenshot_opt_out_overrides_config_default(self):
        Environment.percy_config = {'snapshot': {'dynamicIsland': True}}
        self.assertFalse(self.requested(dynamic_island=False))

    @patch_android_metadata
    def test_not_requested_for_fullpage(self):
        self.assertFalse(self.requested(dynamic_island=True, fullpage=True))

    @patch_android_metadata
    def test_malformed_config_is_ignored(self):
        for config in ({'snapshot': None}, {'snapshot': 'x'}, 'x', {'snapshot': {'dynamicIsland': 'yes'}}):
            Environment.percy_config = config
            self.assertFalse(self.requested(), config)

    def test_options_carry_dynamic_island_when_requested(self):
        self.assertIs(self.sent_options(dynamic_island=True)['dynamicIsland'], True)

    def test_options_omit_dynamic_island_otherwise(self):
        self.assertNotIn('dynamicIsland', self.sent_options())
