import re

def get_col_datatype(col):
    type_name = col.dtype.name
    # Replace numbers e.g the 64 in int64
    type_name = re.sub(r"\d+", "", type_name)

    # Replace anything within square brackets e.g. [ns][us][ms] etc
    # https://github.com/numpy/numpy/blob/453aa08b88cf3497a67abd0ddc115a6a4fc43b81/numpy/ma/core.py#L196

    type_name = re.sub(r"\[\w+\]", "", type_name)

    lookup = {
        "int": "int",
        "float": "float",
        "object": "character",
        "datetime": "datetime",
        "bool": "boolean",
        "long": "long"
    }

    # If values are outside range of ints, use long:

    if type_name == "int":
        if col.abs().max() > 2147483647:
            type_name = "long"

    if type_name in lookup:
        return lookup[type_name]
    else:
        return "character"


def generate_from_pd_df(df):
    """
    Generate barebones metadata from a pandas dataframe.

    Metadata will include 'name' and 'type' fields, but will be missing important elements
    such as 'description' and 'pattern' or 'enum' where relevant.
    """
    metadata = {"columns": []}
    for col in df.columns:
        col_metadata = {"name": col,
                        "description": "",
                        "type": get_col_datatype(df[col])
                        }
        metadata["columns"].append(col_metadata)
    return metadata