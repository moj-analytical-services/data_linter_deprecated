import unittest
import os
import sys
import json
import pandas as pd
from jsonschema.exceptions import ValidationError

from parameterized import parameterized

from data_linter.lint import Linter

cwd = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(__file__))

from testutils import get_test_csv, get_test_jsonl, read_json


class TestLinterMethods(unittest.TestCase):

    def test_validate_meta_data(self):
        meta = read_json(cwd, "meta/test_meta_cols_valid.json")

        #Data is irrelevant but cannot instantiate linter without it
        df = get_test_csv(cwd, "test_csv_data_valid")

        # Test no error is raised
        L = Linter(df, meta)


        # Test invalid metadata raises an error
        meta = read_json(cwd, "meta/test_invalid_meta_cols_missing_name.json")

        with self.assertRaises(ValidationError):
            L = Linter(df, meta)

        # Test invalid metadata raises an error
        meta = read_json(cwd, "meta/test_invalid_meta_columns_key_mispelt.json")

        with self.assertRaises(ValidationError):
            L = Linter(df, meta)
