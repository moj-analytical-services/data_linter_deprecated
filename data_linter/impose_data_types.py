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


def _list_of_date_columns_from_metadata(meta_cols):
    """
    Get list of columns to pass to the pandas.to_csv date_parse argument from table metadata
    """

    parse_dates = []

    for c in meta_cols:
        colname = c["name"]
        coltype = c["type"]

        if coltype in ["date", "datetime"]:
            parse_dates.append(colname)

    return parse_dates



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


def _list_of_date_columns_from_metadata(meta_cols):
    """
    Get list of columns to pass to the pandas.to_csv date_parse argument from table metadata
    """

    parse_dates = []

    for c in meta_cols:
        colname = c["name"]
        coltype = c["type"]

        if coltype in ["date", "datetime"]:
            parse_dates.append(colname)

    return parse_dates


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

    df_cols_set = set(df.columns)
    metadata_date_cols_set = set(
        _list_of_date_columns_from_metadata(meta_cols))
    metadata_cols_set = set([c["name"] for c in meta_cols])

    # Cols that may need conversion minus the date cols
    nondate_columns = df_cols_set.intersection(
        metadata_cols_set) - metadata_date_cols_set

    date_columns = df_cols_set.intersection(metadata_date_cols_set)

    for col in nondate_columns:
        expected_type = _get_np_datatype_from_metadata(col, meta_cols)
        actual_type = df[col].dtype.type

        if expected_type != actual_type:
            df[col] = df[col].astype(expected_type, errors=errors)

        if expected_type == np.typeDict["object"]:
            df[col] = df[col].astype(str)

    for col in date_columns:
        expected_type = np.typeDict["Datetime64"]
        actual_type = df[col].dtype.type

        if expected_type != actual_type:
            # TODO:  The metadata should probably support a datatime format (e.g. '%d/%m/%Y') string, which
            # we attempt to apply here
            df[col] = pd.to_datetime(df[col], errors=errors)

    return df
