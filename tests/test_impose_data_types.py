# -*- coding: utf-8 -*-

import unittest
import pandas as pd
import json
import os
import sys

from data_linter.impose_data_types import impose_metadata_types_on_pd_df, _pd_df_datatypes_match_metadata_data_types

cwd = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(__file__))

from testutils import get_test_csv, get_test_jsonl, read_json

class ConformanceTestOfValidData(unittest.TestCase):
    """
    Tests whether column conformance is successfully imposed when the input data and metadata is valid.
    """

    def test_metadata_correctly_imposed_on_valid_data(self):

        df = get_test_csv(cwd, "test_csv_data_valid")

        meta_data = read_json(cwd, "meta/test_meta_cols_valid.json")

        meta_cols = meta_data["columns"]

        self.assertFalse(
            _pd_df_datatypes_match_metadata_data_types(df, meta_cols))

        # We expect that, after impose_metadata_types_on_pd_df is run, the datatypes conform to the metadata
        df = impose_metadata_types_on_pd_df(df, meta_data)

        self.assertTrue(
            _pd_df_datatypes_match_metadata_data_types(df, meta_cols))

    def test_metadata_correctly_imposed_on_alreadytyped_date(self):

        # What happens if we read in an already typed database
        df = pd.read_parquet(os.path.join(cwd, "data", "test_parquet_data_valid.parquet"))

        meta_data = read_json(cwd, "meta/test_meta_cols_valid.json")

        meta_cols = meta_data["columns"]

        self.assertTrue(
            _pd_df_datatypes_match_metadata_data_types(df, meta_cols))

        # We expect that, after impose_metadata_types_on_pd_df is run, the datatypes conform to the metadata
        df = impose_metadata_types_on_pd_df(df, meta_data)

        self.assertTrue(
            _pd_df_datatypes_match_metadata_data_types(df, meta_cols))

    def test_metadata_impose_does_not_work_on_invalid_data(self):

        # What happens if we read in data that does NOT conform to the metadata
        df = get_test_csv(cwd, "test_csv_data_invalid_data")

        meta_data = read_json(cwd, "meta/test_meta_cols_valid.json")

        meta_cols = meta_data["columns"]

        self.assertFalse(
            _pd_df_datatypes_match_metadata_data_types(df, meta_cols))

        # We expect that, after impose_metadata_types_on_pd_df is run, the datatypes do NOT conform to the metadata
        df = impose_metadata_types_on_pd_df(df, meta_data)

        self.assertFalse(
            _pd_df_datatypes_match_metadata_data_types(df, meta_cols))

    def test_metadata_impose_works_on_non_strings(self):

        #What happens if we read ints and it expects strings?

        df = pd.read_parquet(os.path.join(cwd, "data", "test_parquet_data_valid.parquet"))

        meta_data = read_json(cwd, "meta/test_meta_cols_allstring.json")

        meta_cols = meta_data["columns"]

        self.assertFalse(
            _pd_df_datatypes_match_metadata_data_types(df, meta_cols))

        df = impose_metadata_types_on_pd_df(df, meta_data)

        self.assertTrue(
            _pd_df_datatypes_match_metadata_data_types(df, meta_cols))
