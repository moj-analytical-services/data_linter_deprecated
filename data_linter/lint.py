import pandas as pd
import numpy as np
import great_expectations as ge

class Linter:
    def __init__(self, df, meta):
        """
        Takes a pandas dataframe and a table meta data object and checks
        the values in the dataframe against the meta data.
        """
        self.df = df
        self.meta = meta

    @property
    def df(self):
        return self._df

    @df.setter
    def df(self, df):
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas dataframe object")
        else:
            self._df = ge.from_pandas(df)
    
    @property
    def meta(self):
        return self._meta
    
    @meta.setter
    def meta(self, meta):
        if meta is not None and not isinstance(meta, TableMeta):
            raise TypeError("meta must be a TableMeta object")
        else:
            self._meta = meta
    

    def get_meta_col(self, col_name):
        if col_name not in self.meta.column_names:
            raise ValueError(f"col_name: {col_name} not found in meta data columns.")
        return [c for c in self.meta.columns if c['name'] == col_name][0]

    @property
    def meta_columns(self):
        return self.meta['columns']

    @property
    def meta_column_names(self):
        return [c['name'] for c in self.meta_columns]
    
    def check_column_name_and_order(self):
        self.df.expect_table_columns_to_match_ordered_list(self.meta_column_names)