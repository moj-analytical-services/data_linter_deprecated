import pandas as pd
import numpy as np

from etl_manager.meta import read_table_json, TableMeta

class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class DataframeNotSet(Error):
    """
    Exception raised if df property is None
    """
    def __init__(self, msg=None):
        if msg is None:
            # Set some default useful error message
            msg = "Dataframe has not been set. Use read_df_from_* methods or set df property to a dataframe."
        super(DataframeNotSet, self).__init__(msg)

class TableMetaNotSet(Error):
    """
    Exception raised if table_meta property is None
    """
    def __init__(self, msg=None):
        if msg is None:
            # Set some default useful error message
            msg = "table_meta has not been set. Use read_table_meta method or set table_meta property to a TableMeta objects."
        super(TableMetaNotSet, self).__init__(msg)

class Linter:
    def __init__(self, df=None, table_meta=None):
        """
        Takes a pandas dataframe and a table meta data object and checks
        the values in the dataframe against the meta data.
        """
        self.df = df
        self.table_meta = table_meta

    @property
    def df(self):
        return self._df

    @df.setter
    def df(self, df):
        if df is not None and not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas dataframe object")
        else:
            self._df = df
    
    @property
    def table_meta(self):
        return self._table_meta
    
    @table_meta.setter
    def table_meta(self, table_meta):
        if table_meta is not None and not isinstance(table_meta, TableMeta):
            raise TypeError("table_meta must be a TableMeta object")
        else:
            self._table_meta = table_meta
    
    def test_columns(self):
        """
        Returns test results of each column
        """
        self._check_df_and_meta_are_set()
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
        self._check_df_and_meta_are_set()
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
        self._check_df_and_meta_are_set()
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
        self._check_df_and_meta_are_set()
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
        self._check_df_and_meta_are_set(check_meta=False)
        arr = self.df[col_name].isnull()
        if empty_str_as_null:
            arr = (arr) | (self.df[col_name] == '')
        return arr

    def meta_col(self, col_name):
        self._check_df_and_meta_are_set(check_df=False)
        if col_name not in self.table_meta.column_names:
            raise ValueError(f"col_name: {col_name} not found in meta data columns.")
        return [c for c in self.table_meta.columns if c['name'] == col_name][0]

    def _check_df_and_meta_are_set(self, check_df=True, check_meta=True):
        if check_df and self.df is None:
            raise DataframeNotSet()
        if check_meta and self.table_meta is None:
            raise TableMetaNotSet()

    def read_table_meta(self, path):
        """
        Reads in the table meta data object
        """
        self.table_meta = read_table_json(path)

    def read_df_from_csv(self, path, *args, **kwargs):
        """
        Reads in pandas dataframe from the provided path of a csv file. Args and kwargs are
        passed to pd.read_csv function. Note low_memory is set to False and dtype is set to
        object.
        """
        self.df = pd.read_csv(path, low_memory=False, dtype=object, *args, **kwargs)

    def read_df_from_jsonl(self, path, *args, **kwargs):
        """
        Reads in pandas dataframe from the provided path of a jsonl file. Args and kwargs are 
        passed to pd.read_csv function. Note low_memory is set to False and dtype is set to
        object.
        """
        self.df = pd.read_json(path, dtype=object, lines=True, numpy=True, *args, **kwargs)
