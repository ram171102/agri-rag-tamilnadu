"""Show expected vs retrieved pages for one question.

Usage: python eval\\show.py hybrid q010
"""
import json
import sys

method, qid = sys.argv[1:3]
with open(f"eval/results/{method}.json", encoding="utf-8") as f:
    row = next(r for r in json.load(f) if r["id"] == qid)

print(row["question"])
print("expected:")
for doc, page in row.get("expected", []):
    print(f"  {doc}  p.{page}")
print("retrieved (rank order):")
for rank, (doc, page) in enumerate(row["retrieved"], start=1):
    print(f"  #{rank}  {doc}  p.{page}")