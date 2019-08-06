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


def _get_np_datatype_from_metadata(col_name, meta_cols):
    """
    Lookup the datatype from the metadata, and our conversion table
    """

    with pkg_resources.resource_stream(__name__, "data/data_type_conversion.csv") as io:
        type_conversion = pd.read_csv(io)
    type_conversion = type_conversion.set_index("metadata")
    type_conversion_dict = type_conversion.to_dict(orient="index")

    col = None
    for c in meta_cols:
        if c["name"] == col_name:
            col = c

    if col:
        agnostic_type = col["type"]
        numpy_type = type_conversion_dict[agnostic_type]["pandas"]
        return np.typeDict[numpy_type]
    else:
        return None


def _pd_date_parse_list_from_metadatadata(meta_cols):
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


def impose_metadata_types_on_pd_df(df, meta_cols, errors='ignore'):
    """
    Try to impose correct data type on all columns in metadata.
    Doesn't modify columns not in metadata

    Allows you to pass arguments through to the astype e.g. to errors = 'ignore'
    https://pandas.pydata.org/pandas-docs/stable/generated/pandas.Series.astype.html
    """

    df_cols_set = set(df.columns)
    metadata_date_cols_set = set(
        _pd_date_parse_list_from_metadatadata(meta_cols))
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
