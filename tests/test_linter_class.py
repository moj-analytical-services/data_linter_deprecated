import unittest
import os
import json

from parameterized import parameterized

from data_linter.lint import Linter

current_dir = os.path.dirname(os.path.abspath(__file__))

def get_test_csv(filename):
    path = os.path.join(current_dir, "data", filename)
    return pd.read_csv(path, dtype=object, low_memory=True)

def get_df_from_jsonl(filename):
    path = os.path.join(current_dir, "data", filename)
    return pd.read_json(path, lines=True)

def get_json(filename):
    path = os.path.join(current_dir, "data", filename)
    with open(path) as f:
        o = json.loads(f)
    return o

class TestLinterMethods(unittest.TestCase):
    pass