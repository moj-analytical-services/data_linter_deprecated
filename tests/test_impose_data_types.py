# -*- coding: utf-8 -*-

import unittest
import pandas as pd
import json
import os

from data_linter.impose_data_types import impose_metadata_types_on_pd_df, _pd_df_datatypes_match_metadata_data_types


def read_json_from_path(path):
    with open(path) as f:
        return_json = json.load(f)
    return return_json


THIS_DIR = os.path.dirname(os.path.abspath(__file__))


def td_path(path):
    return os.path.join(THIS_DIR, "data", path)


class ConformanceTest(unittest.TestCase):
    """
    Test packages utilities functions
    """

    def test_metadata_correctly_imposed_on_valid_data(self):

        df = pd.read_csv(td_path("test_csv_data_valid.csv"), dtype="object")

        meta_cols = read_json_from_path(
            td_path("test_table_metadata_valid.json"))

        self.assertFalse(
            _pd_df_datatypes_match_metadata_data_types(df, meta_cols))

        # We expect that, after impose_metadata_types_on_pd_df is run, the datatypes conform to the metadata
        df = impose_metadata_types_on_pd_df(df, meta_cols)

        self.assertTrue(
            _pd_df_datatypes_match_metadata_data_types(df, meta_cols))
