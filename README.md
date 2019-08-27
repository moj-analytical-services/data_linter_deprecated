# data_linter

A python package that validates datasets against a metadata schema which is defined [here](https://github.com/moj-analytical-services/data_linter/blob/master/data_linter/data/metadata_jsonschema.json).

It performs the following checks:
- Are the columns of the correct data types (or can they be converted without error using `pd.Series.astype` in the case of untyped data formats like `csv`)
- Column names:
    - Are the columns named correctly?
    - Are they in the same order specified in the meta data
    - Are there any missing columns?
- Where a regex `pattern` is provided in the metadata,  does the actual data always fit the `pattern`
- Where an `enum` is provided in the metadata, does the actual data contain only values in the `enum`
- Where `nullable` is set to false in the metadata, are there really no nulls in the data?

The package also provides functionality to `impose_metadata_types_on_pd_df`, which allows the user to safely convert a pandas dataframe to the datatypes specified in the metadata.  This is useful in the case you have an untyped data file such as a `csv` and want to ensure it is conformant with the metadata.

## Usage

For detailed information about how to use the package, please see the [demo repo](https://github.com/moj-analytical-services/data_linter_demo).  This includes an interactive tutorial that you can run in your web browser.

Here's a very basic example

```
import pandas as pd
import json

from data_linter.lint import Linter

def read_json_from_path(path):
    with open(path) as f:
        return_json = json.load(f)
    return return_json

meta = read_json_from_path("tests/meta/test_meta_cols_valid.json")
df = pd.read_parquet("tests/data/test_parquet_data_valid.parquet")
l = Linter(df, meta)
l.check_all()
l.markdown_report()
```