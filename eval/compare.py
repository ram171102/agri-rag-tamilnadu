"""Show per-question changes between two eval result files."""
import json
import sys

a_name, b_name = (sys.argv[1:3] + ["naive", "hybrid"])[:2] if len(sys.argv) < 3 else sys.argv[1:3]


def load(name):
    with open(f"eval/results/{name}.json", encoding="utf-8") as f:
        return {r["id"]: r for r in json.load(f)}


a, b = load(a_name), load(b_name)
print(f"{'id':<6}{a_name + ' RR':>12}{b_name + ' RR':>12}   question")
for qid in a:
    if "rr" not in a[qid]:
        continue
    ra, rb = a[qid]["rr"], b[qid]["rr"]
    if ra != rb:
        print(f"{qid:<6}{ra:>12.2f}{rb:>12.2f}   {a[qid]['question'][:60]}")