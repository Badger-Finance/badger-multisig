import json

with open("helpers/chaindata.json") as chaindata:
    labels_json = json.load(chaindata)
    labels = {int(k): v for k, v in labels_json.items()}
