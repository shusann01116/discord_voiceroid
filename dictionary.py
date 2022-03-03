import os
import json
from tokenize import String

path=r"./dict.json"

if os.path.exists(path) is False:
    dic: dict[str, set[dict[str,str]]] = {"word_set": 
        {"sample": "サンプル", "sample2": "サンプル2"}}
    with open(path, mode='w') as f:
        json.dump(dic, f, indent=4)

with open(path) as f:
    dic: dict = json.load(f)
    
word_set: dict = dic.get("word_set")

with open(path) as f:
    dic: dict = json.load(f)

def add(key: String, value: String) -> String:
    word_set[key] = value
    
    with open(path, mode='w') as f:
        json.dump(word_set, f, indent=4)
    return

def remove(key: String):
    del word_set[key]
    
    with open(path, mode='w') as f:
        json.dump(word_set, f, indent=4)
    return
