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
            self._log[c['name']] = {}

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
        # Apply to log not return
        # log["col1"]["check_column_name_and_order"] = BLAH
        return self.df.expect_table_columns_to_match_ordered_list(self.meta_colnames, result_format="COMPLETE", catch_exceptions=True)

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
                
                enum_result = {}
                continue
            
            enum_result = \
            self.df.expect_column_values_to_be_in_set(col["name"],
                                                      enum_list,
                                                      result_format="COMPLETE", 
                                                      include_config=False, 
                                                      catch_exceptions=True)
            
            self.log[col["name"]][test_name] = enum_result
