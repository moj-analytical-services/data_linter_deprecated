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


class TestLogMethods(unittest.TestCase):
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

        df = get_test_csv(cwd, d)
        meta = read_json(cwd, m)
        expected_result = read_json(cwd, r)

        l = Linter(df, meta)
        l.check_enums()
        result = l.vlog["mychar"]["check_enums"].as_dict()
        self.assertDictEqual(result, expected_result)

    # @parameterized.expand(
    #     [
    #         (
    #             "test_csv_data_valid",
    #             "meta/test_meta_cols_valid.json",
    #             "expected_results/test_check_column_exists_and_order/data_valid.json",
    #         ),
    #         (
    #             "test_csv_data_missing_col",
    #             "meta/test_meta_cols_valid.json",
    #             "expected_results/test_check_column_exists_and_order/missing_col.json",
    #         ),
    #         (
    #             "test_csv_data_valid_wrong_order",
    #             "meta/test_meta_cols_valid.json",
    #             "expected_results/test_check_column_exists_and_order/wrong_order.json",
    #         ),
    #     ]
    # )
    # def test_check_column_exists_and_order(self, d, m, r):
    #     df = get_test_csv(d)
    #     meta = read_json(m)
    #     result = read_json(r)
    #     L = Linter(df, meta)
    #     L.check_column_exists_and_order()

    #     self.assertDictEqual(L.log, result)

    # @parameterized.expand(
    #     [
    #         (
    #             "test_csv_data_invalid_regex",
    #             "meta/test_meta_cols_regex.json",
    #             "expected_results/test_result_invalid_regex.json",
    #         )
    #     ]
    # )
    # def test_check_regex(self, d, m, r):

    #     df = get_test_csv(d)
    #     meta = read_json(m)
    #     result = read_json(r)[0]

    #     L = Linter(df, meta)
    #     L.check_pattern()
    #     self.assertDictEqual(L.log, result)

    # def test_validate_meta_data(self):
    #     meta = read_json("meta/test_meta_cols_valid.json")

    #     #Data is irrelevant but cannot instantiate linter without it
    #     df = get_test_csv("test_csv_data_valid")

    #     # Test no error is raised
    #     L = Linter(df, meta)

    #     # Test invalid metadata raises an error
    #     meta = read_json("meta/test_invalid_meta_cols_missing_name.json")

    #     with self.assertRaises(ValidationError):
    #         L = Linter(df, meta)

    #     # Test invalid metadata raises an error
    #     meta = read_json("meta/test_invalid_meta_columns_key_mispelt.json")

    #     with self.assertRaises(ValidationError):
    #         L = Linter(df, meta)
