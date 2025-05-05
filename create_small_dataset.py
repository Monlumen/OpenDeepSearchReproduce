from random import shuffle

path = "./evals/datasets/frames_xxx_set.csv"
from_name = "test"
to_name = "small"

size = 50

with open(path.replace("xxx", from_name), "r", encoding="utf-8") as f:
    lines = [line for line in f]


examples = lines[1:]
shuffle(examples)
lines[1:] = examples

with open(path.replace("xxx", to_name), "w", encoding="utf-8") as f:
    f.write("".join(lines[: size+1]))