import json
import urllib.request

with urllib.request.urlopen("https://raw.githubusercontent.com/moj-analytical-services/etl_manager/master/etl_manager/specs/table_schema.json") as url:
    schema = json.loads(url.read().decode())

schema["title"] = "Schema for column metadata"
schema["description"] = "For use in the python data_linter package"
cols = schema["properties"]["columns"]
schema["properties"] = {}
schema["properties"]["columns"] = cols

# In ETL manager we have a column naming convention, but other uses of the package may not want to be this strict
try:
    del schema["properties"]["columns"]["items"]["properties"]["name"]["pattern"]
except:
    pass

with open("data_linter/data/metadata_jsonschema.json", "w") as f:
    json.dump(schema, f, indent=4)
