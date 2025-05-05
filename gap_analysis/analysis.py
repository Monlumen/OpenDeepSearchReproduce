import json
import os

print(os.getcwd())

path_std = "./gap_analysis/std_output.jsonl"
path_rep = "./gap_analysis/this_output.jsonl"

def get_entries(path: str):
    with open(path, "r", encoding="utf-8") as f:
        objs = [json.loads(line.strip()) for line in f]
    return objs

rep_entries = get_entries(path_rep)
std_entries = get_entries(path_std)