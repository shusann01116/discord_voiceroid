import os
import json
from typing import Dict
import pprint

path = r"./ignore.json"

if os.path.exists(path) is False:
    ignores: dict = {"start_with" : ["<", "http"]}
    with open(path, mode='w') as f:
        json.dump(ignores, f, indent=4)

with open(path) as f:
    ignores: dict = json.load(f)

start_with = ignores.get("start_with")

def add_ignore(word: dict) -> None:
    for key, value in word.items():
        values = ignores[key]
        values += value
        ignores.update({key: values})

    with open(path, mode='w') as f:
        json.dump(ignores, f, indent=4)

def remove_ignore(word: dict) -> None:
    for key, value in word.items():
        values = ignores[key]
        values = [result for result in values if result != value]
        ignores.update({key: values})

    with open(path, mode='w') as f:
        json.dump(ignores, f, indent=4)
