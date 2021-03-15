import json


def read_json_file(file):
    with open(file) as f:
        content = json.load(f)
    return content
