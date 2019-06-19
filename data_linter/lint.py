import pandas as pd
import numpy as np

from etl_manager.meta import read_table_json

class Linter:
    def __init__(self, datapath, metapath):
        self.datapath = datapath,
        self.metapath = metapath,
        self.df = pd.read_csv(datapath, low_memory=False, dtype=object)
        self.table_meta = read_table_json(metapath)

    def test_columns(self):
        """
        Returns test results of each column
        """
        resp = {}

        for c in self.table_meta.column_names:
            resp[c] = {
                "nullable": np.all(self.check_nullable_values(c)),
                "enum": np.all(self.check_enum_values(c)),
                "regex": np.all(self.check_regex_values(c)),
            }
        
        return resp

    def check_enum_values(self, col_name):
        """
        Returns a numpy boolean array. True if value is present in enum False
        if not for each value in the column. Returns null if metadata has
        no enum property for that column. Treats nulls as passes.

        col_name: (String) name of the column to test.
        """
        m = self.meta_col(col_name)
        if 'enum' not in m:
            return None
        else:
            return self.df[col_name].isin(m['enum'])

    def check_regex_values(self, col_name):
        """
        Returns a numpy boolean array of that is True (matches regex expr) or
        False (doesn't match regex expr) for each value in the column. Returns null
        if metadata has no regex expr for that column. Treats na's as passes.

        col_name: (String) name of the column to test.
        """
        m = self.meta_col(col_name)
        if 'regex' not in m:
            return None
        else:
            return self.df[col_name].str.contains(m['regex'], na=True, regex=True)

    def check_nullable_values(self, col_name, empty_str_as_null=False):
        """
        Returns a numpy boolean array of that tests each value of the column
        against the meta data column definition. If nullable in meta is True
        then will return all values as True. If nullable is False will return
        the inverse of the get_nullable_values function. Will return null if
        meta has no nullable property then.

        col_name: (String) name of the column to test.
        """
        m = self.meta_col(col_name)
        if 'nullable' not in m:
            return None
        elif m['nullable']:
            return np.repeat(True, len(self.df))
        else:
            nulls = self.get_nullable_values(col_name, empty_str_as_null)
            return np.invert(nulls)
            
    def get_nullable_values(self, col_name, empty_str_as_null=False):
        """
        Returns a numpy boolean array of that is True (in null value) or
        False (not null) for each value in the column. Returns null
        if metadata has no nullable parameter.

        col_name: (String) name of the column to test.
        """
        arr = self.df[col_name].isnull()
        if empty_str_as_null:
            arr = (arr) | (self.df[col_name] == '')
        return arr

    def meta_col(self, col_name):
        if col_name not in self.table_meta.column_names:
            raise ValueError(f"col_name: {col_name} not found in meta data columns.")
        return [c for c in self.table_meta.columns if c['name'] == col_name][0]
