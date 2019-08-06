# data_linter

A python package that validates datasets against a metadata schema.

It performs the following checks:
- Are the columns of the correct data types (or can they be converted without error using `pd.Series.astype`)
- Column names:
    - Are the columns named correctly?
    - Are they in the same order specified in the meta data
    - Are there any missing columns?
    - Are there any superfluous columns?
- Where a regex `pattern` is provided in the metadata,  does the actual data always fit the `pattern`
- Where an `enum` is provided in the metadata, does the actual data contain only values in the `enum`
- Where `nullable` is set to false in the metadata, are there really no nulls in the data?

The package also provides functionality to `impose_metadata_types_on_pd_df`, which allows the user to safely convert a pandas dataframe to the datatypes specified in the metadata.


TODO: Describe metadata - is the current `jsonschema` valid?