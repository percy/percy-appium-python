import unittest

from percy.lib.ignore_region import IgnoreRegion

class TestIgnoreRegion(unittest.TestCase):

    def test_ignore_region_valid_input(self):
        # test with valid input
        top, bottom, left, right = 10, 20, 30, 40
        ignore_region = IgnoreRegion(top, bottom, left, right)

        # check that the ignore region attributes are set correctly
        self.assertEqual(ignore_region.top, top)
        self.assertEqual(ignore_region.bottom, bottom)
        self.assertEqual(ignore_region.left, left)
        self.assertEqual(ignore_region.right, right)

    def test_ignore_region_negative_input(self):
        # test with negative input
        with self.assertRaises(ValueError):
            IgnoreRegion(-10, 20, 30, 40)
        with self.assertRaises(ValueError):
            IgnoreRegion(10, 20, -30, 40)
        with self.assertRaises(ValueError):
            IgnoreRegion(10, 20, 30, -40)
        with self.assertRaises(ValueError):
            IgnoreRegion(-10, -20, -30, -40)

    def test_ignore_region_invalid_input(self):
        # test with invalid input
        with self.assertRaises(ValueError):
            IgnoreRegion(20, 10, 30, 40) # bottom < top
        with self.assertRaises(ValueError):
            IgnoreRegion(10, 20, 40, 30) # right < left

    def test_ignore_region_is_valid(self):
        # test the is_valid method with a valid ignore region and valid screen size
        ignore_region = IgnoreRegion(10, 20, 30, 40)
        screen_height, screen_width = 100, 200
        self.assertTrue(ignore_region.is_valid(screen_height, screen_width))

        # test the is_valid method with an invalid ignore region and valid screen size
        ignore_region = IgnoreRegion(10, 200, 30, 400)
        height, width = 100, 200
        self.assertFalse(ignore_region.is_valid(height, width))

        # test the is_valid method with a valid ignore region and invalid screen size
        ignore_region = IgnoreRegion(10, 20, 30, 40)
        screen_height, screen_width = 5, 10
        self.assertFalse(ignore_region.is_valid(screen_height, screen_width))

if __name__ == '__main__':
    unittest.main()
