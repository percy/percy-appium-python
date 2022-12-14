import unittest
from percy.lib.percy_options import PercyOptions


class TestPercyOptions(unittest.TestCase):
    def test_percy_options_not_provided(self):  # Defaults
        capabilities = {}
        percy_options = PercyOptions(capabilities)
        self.assertTrue(percy_options.enabled)
        self.assertTrue(percy_options.ignore_errors)

    def test_percy_options_w3c_enabled(self):
        capabilities = {'percy:options': {'enabled': True}}
        percy_options = PercyOptions(capabilities)
        self.assertTrue(percy_options.enabled)
        self.assertTrue(percy_options.ignore_errors)

    def test_percy_options_json_wire_enabled(self):
        capabilities = {'percy.enabled': True}
        percy_options = PercyOptions(capabilities)
        self.assertTrue(percy_options.enabled)
        self.assertTrue(percy_options.ignore_errors)

    def test_percy_options_w3c_not_enabled(self):
        capabilities = {'percy:options': {'enabled': False}}
        percy_options = PercyOptions(capabilities)
        self.assertFalse(percy_options.enabled)
        self.assertTrue(percy_options.ignore_errors)

    def test_percy_options_json_wire_not_enabled(self):
        capabilities = {'percy.enabled': False}
        percy_options = PercyOptions(capabilities)
        self.assertFalse(percy_options.enabled)
        self.assertTrue(percy_options.ignore_errors)

    def test_percy_options_w3c_ignore_errors(self):
        capabilities = {'percy:options': {'ignoreErrors': True}}
        percy_options = PercyOptions(capabilities)
        self.assertTrue(percy_options.ignore_errors)
        self.assertTrue(percy_options.enabled)

    def test_percy_options_json_wire_ignore_errors(self):
        capabilities = {'percy.ignoreErrors': True}
        percy_options = PercyOptions(capabilities)
        self.assertTrue(percy_options.ignore_errors)
        self.assertTrue(percy_options.enabled)

    def test_percy_options_w3c_not_ignore_errors(self):
        capabilities = {'percy:options': {'ignoreErrors': False}}
        percy_options = PercyOptions(capabilities)
        self.assertFalse(percy_options.ignore_errors)
        self.assertTrue(percy_options.enabled)

    def test_percy_options_json_wire_not_ignore_errors(self):
        capabilities = {'percy.ignoreErrors': False}
        percy_options = PercyOptions(capabilities)
        self.assertFalse(percy_options.ignore_errors)
        self.assertTrue(percy_options.enabled)

    def test_percy_options_w3c_all_options_false(self):
        capabilities = {'percy:options': {'ignoreErrors': False, 'enabled': False}}
        percy_options = PercyOptions(capabilities)
        self.assertFalse(percy_options.ignore_errors)
        self.assertFalse(percy_options.enabled)

    def test_percy_options_json_wire_all_options_false(self):
        capabilities = {'percy.ignoreErrors': False, 'percy.enabled': False}
        percy_options = PercyOptions(capabilities)
        self.assertFalse(percy_options.ignore_errors)
        self.assertFalse(percy_options.enabled)

    def test_percy_options_w3c_all_options_true(self):
        capabilities = {'percy:options': {'ignoreErrors': True, 'enabled': True}}
        percy_options = PercyOptions(capabilities)
        self.assertTrue(percy_options.ignore_errors)
        self.assertTrue(percy_options.enabled)

    def test_percy_options_json_wire_all_options_true(self):
        capabilities = {'percy.ignoreErrors': True, 'percy.enabled': True}
        percy_options = PercyOptions(capabilities)
        self.assertTrue(percy_options.ignore_errors)
        self.assertTrue(percy_options.enabled)

    def test_percy_options_json_wire_and_w3c_case_1(self):
        capabilities = {'percy.ignoreErrors': False, 'percy:options': {'enabled': False}}
        percy_options = PercyOptions(capabilities)
        self.assertTrue(percy_options.ignore_errors)
        self.assertFalse(percy_options.enabled)

    def test_percy_options_json_wire_and_w3c_case_2(self):
        capabilities = {'percy.enabled': False, 'percy:options': {'ignoreErrors': False}}
        percy_options = PercyOptions(capabilities)
        self.assertFalse(percy_options.ignore_errors)
        self.assertTrue(percy_options.enabled)
