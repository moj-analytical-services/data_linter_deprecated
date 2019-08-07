import unittest
import os
import json
import pandas as pd
from jsonschema.exceptions import ValidationError

from parameterized import parameterized

from data_linter.lint import Linter

current_dir = os.path.dirname(os.path.abspath(__file__))


def get_test_csv(filename):
    path = os.path.join(current_dir, "data", filename + ".csv")
    return pd.read_csv(path, dtype=object, low_memory=True)


def get_test_jsonl(filename):
    path = os.path.join(current_dir, "data", filename + ".jsonl")
    return pd.read_json(path, lines=True)


def read_json(rel_path):
    path = os.path.join(current_dir, rel_path)
    with open(path) as f:
        o = json.load(f)
    return o


class TestLinterMethods(unittest.TestCase):
    @parameterized.expand(
        [
            (
                "test_csv_data_invalid_enums",
                "meta/test_meta_cols_enums.json",
                "expected_results/test_result_invalid_enums.json",
            ),
            (
                "test_csv_data_valid_enums",
                "meta/test_meta_cols_enums.json",
                "expected_results/test_result_valid_enums.json",
            ),
        ]
    )
    def test_check_enums(self, d, m, r):

        df = get_test_csv(d)
        meta = read_json(m)
        result = read_json(r)[0]

        L = Linter(df, meta)
        L.check_enums()
        self.assertDictEqual(L.log, result)

    @parameterized.expand(
        [
            (
                "test_csv_data_valid",
                "meta/test_meta_cols_valid.json",
                "expected_results/test_check_column_exists_and_order/data_valid.json",
            ),
            (
                "test_csv_data_missing_col",
                "meta/test_meta_cols_valid.json",
                "expected_results/test_check_column_exists_and_order/missing_col.json",
            ),
            (
                "test_csv_data_valid_wrong_order",
                "meta/test_meta_cols_valid.json",
                "expected_results/test_check_column_exists_and_order/wrong_order.json",
            ),
        ]
    )
    def test_check_column_exists_and_order(self, d, m, r):
        df = get_test_csv(d)
        meta = read_json(m)
        result = read_json(r)
        L = Linter(df, meta)
        L.check_column_exists_and_order()

        self.assertDictEqual(L.log, result)

    @parameterized.expand(
        [
            (
                "test_csv_data_invalid_regex",
                "meta/test_meta_cols_regex.json",
                "expected_results/test_result_invalid_regex.json",
            )
        ]
    )
    def test_check_regex(self, d, m, r):

        df = get_test_csv(d)
        meta = read_json(m)
        result = read_json(r)[0]

        L = Linter(df, meta)
        L.check_pattern()
        self.assertDictEqual(L.log, result)

    def test_validate_meta_data(self):
        meta = read_json("meta/test_meta_cols_valid.json")

        #Data is irrelevant but cannot instantiate linter without it
        df = get_test_csv("test_csv_data_valid")

        # Test no error is raised
        L = Linter(df, meta)


        # Test invalid metadata raises an error
        meta = read_json("meta/test_invalid_meta_cols_missing_name.json")

        with self.assertRaises(ValidationError):
            L = Linter(df, meta)

        # Test invalid metadata raises an error
        meta = read_json("meta/test_invalid_meta_columns_key_mispelt.json")

        with self.assertRaises(ValidationError):
            L = Linter(df, meta)
