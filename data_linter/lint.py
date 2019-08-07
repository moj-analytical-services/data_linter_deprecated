import great_expectations as ge
import json
import jsonschema
import numpy as np
import pandas as pd
import pkg_resources
from data_linter.impose_data_types import impose_metadata_types_on_pd_df
from data_linter.validation_log import ValidationLog


class Linter:
    def __init__(self, df, meta_data):
        """
        Takes a pandas dataframe and a table meta data object and checks
        the values in the dataframe against the meta data.
        """
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas dataframe object")

        self.meta_data = meta_data
        self.validate_meta_data()

        self.meta_cols = meta_data["columns"]
        # Placeholer for proper schema check
        if not isinstance(self.meta_cols, list):
            raise TypeError("meta_cols must be a list of objects")

        # This never fails, but the resultant types are not guaranteed to be correct
        df = impose_metadata_types_on_pd_df(df, meta_data)

        self.df_ge = ge.from_pandas(df)

        self.vlog = ValidationLog(self)

        self.log = {}
        for c in self.meta_cols:
            self.log[c["name"]] = {}


    def get_meta_col(self, col_name):
        if col_name not in self.meta_colnames:
            raise ValueError(f"col_name: {col_name} not found in meta data columns.")
        return [c for c in self.meta_cols if c["name"] == col_name][0]

    @property
    def meta_colnames(self):
        return [c["name"] for c in self.meta_cols]

    def _get_template_result(self):
        return {"success": None, "result": {}}

    def check_column_exists_and_order(self):
        """
        Checks if columns in meta data exist in dataframe and also checks if dataframe order is correct.
        writes results of tests to log property
        """
        fn = "check_column_exists_and_order"

        # Create lookup for df cols
        df_cols = {}
        for i, c in enumerate(self.df_ge.columns):
            df_cols[c] = i

        #  Test meta cols
        for i, c in enumerate(self.meta_colnames):
            self.log[c][fn] = self._get_template_result()
            self.log[c][fn]["result"]["expected_pos"] = i

            if c in df_cols:
                self.log[c][fn]["result"]["column_exists"] = True
                self.log[c][fn]["result"]["actual_pos"] = df_cols[c]
                self.log[c][fn]["result"]["order_match"] = i == df_cols[c]
            else:
                self.log[c][fn]["result"]["column_exists"] = False
                self.log[c][fn]["result"]["actual_pos"] = None
                self.log[c][fn]["result"]["order_match"] = False

            self.log[c][fn]["success"] = (
                self.log[c][fn]["result"]["column_exists"]
                and self.log[c][fn]["result"]["order_match"]
            )


    def check_enums(self):
        """
        Test to if values in column are all in
        enums as specified in metadata
        """
        print("Running enum test")
        test_name = "check_enums"

        for col in self.meta_cols:
            try:
                enum_list = col["enum"]
            except KeyError:
                self.log[col["name"]][test_name] = self._get_template_result()
                continue

            enum_result = self.df_ge.expect_column_values_to_be_in_set(
                col["name"],
                enum_list,
                result_format="COMPLETE",
                include_config=False,
                catch_exceptions=True,
            )

            self.log[col["name"]][test_name] = enum_result

    def check_pattern(self):
        """
        Test to if values in column all fit within
        regex pattern as specified in metadata
        """
        print("Running pattern test")
        test_name = "check_pattern"

        for col in self.meta_cols:
            try:
                pattern = col["pattern"]
            except KeyError:
                self.log[col["name"]][test_name] = self._get_template_result()
                continue

            pattern_result = self.df_ge.expect_column_values_to_match_regex(
                col["name"],
                pattern,
                result_format="COMPLETE",
                include_config=False,
                catch_exceptions=True
            )

            self.log[col["name"]][test_name] = pattern_result


    def check_nulls(self):
        """
        Test column for null values
        consistent with nullable property in metadata
        """
        test_name = "check_nulls"

        for col in self.meta_cols:
            nullable = col.get("nullable", True)

            nulls_result = self.df_ge.expect_column_values_to_not_be_null(
                col["name"],
                result_format="COMPLETE",
                include_config=False,
                catch_exceptions=True,
            )

            # Set success property dependent on nullable from metadata
            if nullable:
                nulls_result["success"] = True

            self.log[col["name"]][test_name] = nulls_result

    def validate_meta_data(self):
        """
        Check that the metadata the user has provided is valid
        """
        with pkg_resources.resource_stream(__name__, "data/metadata_jsonschema.json") as io:
            schema = json.load(io)
        jsonschema.validate(self.meta_data, schema)

    def check_all(self):
        """
        Perform all validations, ouputting to linter.log
        """

        self.check_column_exists_and_order()
        self.check_nulls()
        self.check_pattern()
        self.check_enums()
