import ast
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACKAGE = 'appium-python-client'


def _specifier(requirement):
    return re.sub(r'\s+', '', requirement).lower().replace(PACKAGE, '', 1)


class TestRequirements(unittest.TestCase):
    def _setup_py_requirement(self):
        with open(os.path.join(ROOT, 'setup.py'), encoding='utf-8') as f:
            tree = ast.parse(f.read())
        for node in ast.walk(tree):
            if isinstance(node, ast.keyword) and node.arg == 'install_requires':
                for item in ast.literal_eval(node.value):
                    if item.lower().startswith(PACKAGE):
                        return item
        return None

    def _requirements_txt_requirement(self):
        with open(os.path.join(ROOT, 'requirements.txt'), encoding='utf-8') as f:
            for line in f:
                if line.strip().lower().startswith(PACKAGE):
                    return line.strip()
        return None

    def test_appium_client_is_bounded_and_consistent(self):
        from_setup = self._setup_py_requirement()
        from_txt = self._requirements_txt_requirement()
        self.assertEqual(_specifier(from_setup), _specifier(from_txt))
        self.assertIn('<', _specifier(from_txt))
        self.assertIn('>=', _specifier(from_txt))
