# -*- coding: utf-8 -*-

"""
data_linter.impose_data_types
~~~~~~~~~~~~~~~
This module contains functions that impose the datatypes specified in the metadata onto
the dataset which has been imported into the linter
This is needed because, in the case of text-based files like csv, we import the data as
strings rather than let pandas attempt to guess types
"""

import pkg_resources
import pandas as pd
import numpy as np
import json


def _pd_df_datatypes_match_metadata_data_types(df, meta_cols):
    """
    Do the data types in the pandas dataframe match those in meta_cols
    """

    expected_dtypes = _pd_dtype_dict_from_metadata(meta_cols)

    actual_numpy_types = dict(df.dtypes)

    for dt in actual_numpy_types:
        actual_numpy_types[dt] = actual_numpy_types[dt].type

    return actual_numpy_types == expected_dtypes

def get_type_conversion_dict():
    with pkg_resources.resource_stream(__name__, "data/type_conversion.json") as io:
        type_conversion_dict = json.load(io)
    return type_conversion_dict

def _pd_dtype_dict_from_metadata(meta_cols):
    """
    Convert the table metadata to the dtype dict that needs to be
    passed to the dtype argument of pd.read_csv
    """

    type_conversion_dict = get_type_conversion_dict()

    dtype = {}

    for c in meta_cols:
        colname = c["name"]
        coltype = c["type"]
        coltype = type_conversion_dict[coltype]['pd_datatype']
        dtype[colname] = np.typeDict[coltype]

    return dtype

def _get_np_datatype_from_metadata(col_name, meta_cols):
    """
    Lookup the datatype from the metadata, and our conversion table
    """

    with pkg_resources.resource_stream(__name__, "data/type_conversion.json") as io:
        type_conversion_dict = json.load(io)


    # Find the specific col_name in the meta_cols array
    col = None
    for c in meta_cols:
        if c["name"] == col_name:
            col = c

    if col:
        agnostic_type = col["type"]
        numpy_type = type_conversion_dict[agnostic_type]["pd_datatype"]
        return np.typeDict[numpy_type]
    else:
        return None


def convert_int_column(series, errors):
    # Running astype("Int64") on a series with character values always fails
    series[pd.notnull(series)] = series[pd.notnull(series)].astype(int, errors=errors)
    series = series.astype("Int64", errors=errors)
    return series


def impose_metadata_types_on_pd_df(df, meta_data, errors='ignore'):
    """
    Try to impose correct data type on all columns in metadata.
    Doesn't modify columns not in metadata
    Makes a copy of the dataframe (does not modify in place)


    Allows you to pass arguments through to the astype e.g. to errors = 'ignore'
    https://pandas.pydata.org/pandas-docs/stable/generated/pandas.Series.astype.html
    """
    df = df.copy()

    meta_cols = meta_data["columns"]

    for col in meta_cols:
        coltype = col["type"]
        colname = col["name"]
        if colname not in df.columns:
            # There's a column in the metadata that's not in the df
            continue
        expected_type = _get_np_datatype_from_metadata(colname, meta_cols)
        actual_type = df[colname].dtype.type

        if coltype not in ["date", "datetime", "int", "Int64", "character"]:
            if expected_type != actual_type:
                df[colname] = df[colname].astype(expected_type, errors=errors)
        elif coltype == "character":
            if expected_type != actual_type:
                df[colname] = df[colname].astype(str, errors=errors)
        elif coltype == "int":
            df[colname] = convert_int_column(df[colname], errors=errors)
        elif coltype in ["date", "datetime"]:
            # TODO:  The metadata should probably support a datatime format (e.g. '%d/%m/%Y') string, which
            # we attempt to apply here
            df[colname] = pd.to_datetime(df[colname], errors=errors)

    return df
