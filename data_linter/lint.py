import pandas as pd
import numpy as np
import great_expectations as ge

class Linter:
    def __init__(self, df, meta_cols):
        """
        Takes a pandas dataframe and a table meta data object and checks
        the values in the dataframe against the meta data.
        """
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas dataframe object")

        # Placeholer for proper schema check
        if not isinstance(meta_cols, list):
            raise TypeError("meta_cols must be a list of objects")

        self._df = ge.from_pandas(df)
        self._meta_cols = meta_cols

        self._log = {}
        for c in meta_cols:
            self._log[c['name']] = None

    @property
    def df(self):
        return self._df

    @property
    def meta_cols(self):
        return self._meta_cols

    @property
    def log(self):
        return self._log

    def get_meta_col(self, col_name):
        if col_name not in self.meta_colnames:
            raise ValueError(f"col_name: {col_name} not found in meta data columns.")
        return [c for c in self.meta_cols if c['name'] == col_name][0]

    @property
    def meta_colnames(self):
        return [c['name'] for c in self.meta_cols]

    def check_column_name_and_order(self):
        self.df.expect_table_columns_to_match_ordered_list(self.meta_colnames)