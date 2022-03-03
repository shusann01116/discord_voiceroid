import os
import json
from tokenize import String

path = r"./dict.json"

if os.path.exists(path) is False:
    dic = {"word_set": {"sample": "サンプル", "sample2": "サンプル2"}, }
    with open(path, mode='w') as f:
        json.dump(dic, f, indent=4)

with open(path) as f:
    dic: dict = json.load(f)

word_set: dict = dic.get("word_set")
ignore: dict = dic.get("ignore")
start_with: dict = ignore["start_with"]


def add(key: String, value: String) -> String:
    word_set[key] = value
    dic["word_set"] = word_set

    with open(path, mode='w') as f:
        json.dump(dic, f, indent=4)
    return


def remove(key: String):
    del word_set[key]
    dic["word_set"] = word_set

    with open(path, mode='w') as f:
        json.dump(dic, f, indent=4)
    return
