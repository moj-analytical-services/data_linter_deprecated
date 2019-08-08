import os
import pandas as pd
import json

def get_test_csv(current_dir, filename):
    path = os.path.join(current_dir, "data", filename + ".csv")
    return pd.read_csv(path, dtype=object, low_memory=True)


def get_test_jsonl(current_dir, filename):
    path = os.path.join(current_dir, "data", filename + ".jsonl")
    return pd.read_json(path, lines=True)


def read_json(current_dir, rel_path):
    path = os.path.join(current_dir, rel_path)
    with open(path) as f:
        o = json.load(f)
    return o
