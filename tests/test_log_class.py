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
        df = get_test_csv(cwd, d)
        meta = read_json(cwd, m)
        expected_result = read_json(cwd, r)
        l = Linter(df, meta)
        l.check_column_exists_and_order()
        result = l.vlog.as_dict()
        self.assertDictEqual(result, expected_result)

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

        df = get_test_csv(cwd,d)
        meta = read_json(cwd,m)
        expected_result = read_json(cwd,r)

        l = Linter(df, meta)
        l.check_pattern()
        result = l.vlog.as_dict()
        self.assertDictEqual(result, expected_result)


    @parameterized.expand(
        [
            (
                "test_csv_data_valid",
                "meta/test_meta_cols_valid.json",
                True
            ),
            (
                "test_csv_utf8_strings",
                "meta/test_meta_cols_utf8_strings.json",
                True
            ),
            (   "test_csv_data_ints",
                "meta/test_meta_cols_ints.json",
                False
            ),
            (  "test_csv_data_dates",
                "meta/test_meta_cols_dates.json",
                False
             )
        ]
    )
    def test_data_types(self, d, m, r):
        df = get_test_csv(cwd, d)
        meta = read_json(cwd, m)

        l = Linter(df, meta)

        l.check_types()
        result = l.success()
        self.assertEqual(result, r)

    def test_data_types_ints(self):

        df = get_test_csv(cwd, "test_csv_data_ints")
        meta = read_json(cwd, "meta/test_meta_cols_ints.json")

        l = Linter(df, meta)

        l.check_types()

        actual = {k: v["check_data_type"]["success"]
            for k, v in l.vlog.as_dict().items()}

        expected = {'int_with_float': False,
                    'int_with_long': False,
                    'int_with_null': True,
                    'int_without_null': True}

        self.assertDictEqual(actual, expected)


    @parameterized.expand(
        [
            (
                "test_csv_data_valid",
                "meta/test_meta_cols_valid.json",
                True
            ),
            (
                "test_csv_data_missing_col",
                "meta/test_meta_cols_valid.json",
                False
            ),
        ]
    )
    def test_overall_success(self, d, m, r):
        df = get_test_csv(cwd, d)
        meta = read_json(cwd, m)

        l = Linter(df, meta)
        # Should not return success before tests run
        with self.assertRaises(Exception):
            l.success()

        l.check_all()
        result = l.success()
        self.assertEqual(result, r)


    @parameterized.expand(
        [
            ("test_csv_data_additional_col", "meta/test_meta_cols_valid.json"),
            ("test_csv_data_dates", "meta/test_meta_cols_dates.json"),
            ("test_csv_data_ints", "meta/test_meta_cols_ints.json"),
            ("test_csv_data_invalid_data", "meta/test_meta_cols_valid.json"),
            ("test_csv_data_invalid_enums", "meta/test_meta_cols_enums.json"),
            ("test_csv_data_invalid_regex", "meta/test_meta_cols_regex.json"),
            ("test_csv_data_missing_col", "meta/test_meta_cols_valid.json"),
            ("test_csv_data_mixedtype_col", "meta/test_meta_cols_valid.json"),
            ("test_csv_data_valid", "meta/test_meta_cols_valid.json"),
            ("test_csv_data_valid_enums", "meta/test_meta_cols_enums.json"),
            ("test_csv_data_valid_wrong_order", "meta/test_meta_cols_valid.json"),
            ("test_csv_utf8_strings", "meta/test_meta_cols_valid.json")
        ]
    )
    def test_detailed_markdown(self, d, m):
        """
        This tests that a wide range of metadata/data combinations render correctly without erroring
        """

        df = get_test_csv(cwd, d)
        meta = read_json(cwd, m)

        l = Linter(df, meta)

        l.check_all()

        l.markdown_report()






