import unittest
import os
import sys
import json
import pandas as pd
from jsonschema.exceptions import ValidationError

from parameterized import parameterized

from data_linter.generate_meta_data import generate_from_pd_df

cwd = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(__file__))

from testutils import get_test_csv, get_test_jsonl, read_json


class TestGenerateMetadata(unittest.TestCase):

    def test_check_enums(self):

        df = pd.read_csv(os.path.join(
            cwd, "data/test_csv_data_valid.csv"),  parse_dates=["mydatetime", "mydate"])

        expected_result = read_json(cwd, "expected_results/test_result_generated_metadata.json")
        result = generate_from_pd_df(df)

        self.assertDictEqual(result, expected_result)
