import pandas as pd
import numpy as np
import great_expectations as ge

from etl_manager.meta import read_table_json, TableMeta

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
            self._df = df
    
    @property
    def meta(self):
        return self._meta
    
    @meta.setter
    def meta(self, meta):
        if meta is not None and not isinstance(meta, TableMeta):
            raise TypeError("meta must be a TableMeta object")
        else:
            self._meta = meta
    
    def meta_col(self, col_name):
        if col_name not in self.meta.column_names:
            raise ValueError(f"col_name: {col_name} not found in meta data columns.")
        return [c for c in self.meta.columns if c['name'] == col_name][0]