import unittest

import os
from data_linter.lint import Linter

class BasicDataTest(unittest.TestCase):

    def test_pass_response(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(current_dir, 'data/pass_data.csv')
        meta_path = os.path.join(current_dir, 'data/meta.json')

        dl = Linter(data_path, meta_path)
        resp = dl.test_columns()
        expected = {
            "col1": {
                "enum": None,
                "regex": None,
                "nullable": True,
            },
            "col2": {
                "enum": True,
                "regex": None,
                "nullable": None,
            },
            "col3": {
                "enum": None,
                "regex": True,
                "nullable": True,
            }
        }
        self.assertDictEqual(expected['col1'], resp['col1'])
        self.assertDictEqual(expected['col2'], resp['col2'])
        self.assertDictEqual(expected['col3'], resp['col3'])

    def test_fail_response(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(current_dir, 'data/fail_data.csv')
        meta_path = os.path.join(current_dir, 'data/meta.json')

        dl = Linter(data_path, meta_path)
        resp = dl.test_columns()
        expected = {
            "col1": {
                "enum": None,
                "regex": None,
                "nullable": False,
            },
            "col2": {
                "enum": False,
                "regex": None,
                "nullable": None,
            },
            "col3": {
                "enum": None,
                "regex": False,
                "nullable": True,
            }
        }
        self.assertDictEqual(expected['col1'], resp['col1'])
        self.assertDictEqual(expected['col2'], resp['col2'])
        self.assertDictEqual(expected['col3'], resp['col3'])