import unittest

from percy.lib.tile import Tile


class TileTestCase(unittest.TestCase):
    def setUp(self):
        self.tile = Tile(20, 120, 150, 0, filepath='some-file-path', sha='some-sha')
        self.dict_tile = dict(self.tile)

    def test_tile_dict_keys(self):
        self.assertDictEqual(self.dict_tile, self.tile.__dict__)
        self.assertIn('filepath', self.dict_tile)
        self.assertIn('status_bar_height', self.dict_tile)
        self.assertIn('nav_bar_height', self.dict_tile)
        self.assertIn('header_height', self.dict_tile)
        self.assertIn('footer_height', self.dict_tile)
        self.assertIn('fullscreen', self.dict_tile)
        self.assertIn('sha', self.dict_tile)

    def test_tile_values(self):
        self.assertEqual(self.dict_tile['filepath'], 'some-file-path')
        self.assertEqual(self.dict_tile['status_bar_height'], 20)
        self.assertEqual(self.dict_tile['nav_bar_height'], 120)
        self.assertEqual(self.dict_tile['header_height'], 150)
        self.assertEqual(self.dict_tile['footer_height'], 0)
        self.assertEqual(self.dict_tile['sha'], 'some-sha')
        self.assertEqual(self.dict_tile['fullscreen'], False)  # Default
