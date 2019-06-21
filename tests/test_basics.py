import unittest
import os

from parameterized import parameterized

from data_linter.lint import Linter, DataframeNotSet, TableMetaNotSet

class BasicDataTest(unittest.TestCase):


    @parameterized.expand(['csv', 'jsonl'])
    def test_pass_response(self, file_type):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        meta_path = os.path.join(current_dir, 'data/meta.json')
        data_path = os.path.join(current_dir, f"data/pass_data.{file_type}")

        dl = Linter()

        # pass get and exec read_df_from_jsonl or read_df_from_csv depending on input
        getattr(dl, f"read_df_from_{file_type}")(data_path)
        dl.read_table_meta(meta_path)
        
        dl.read_table_meta(meta_path)

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

    @parameterized.expand(['csv', 'jsonl'])
    def test_fail_response(self, file_type):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        meta_path = os.path.join(current_dir, 'data/meta.json')
        data_path = os.path.join(current_dir, f"data/fail_data.{file_type}")
        
        dl = Linter()

        # pass get and exec read_df_from_jsonl or read_df_from_csv depending on input
        getattr(dl, f"read_df_from_{file_type}")(data_path)
        dl.read_table_meta(meta_path)

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

class TestErrors(unittest.TestCase):
    def test_errors(self):
        dl = Linter()
        self.assertRaises(DataframeNotSet, dl.get_nullable_values, "col1")
        self.assertRaises(TableMetaNotSet, dl.meta_col, "col1")
