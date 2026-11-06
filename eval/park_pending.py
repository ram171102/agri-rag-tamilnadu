"""Move questions that still have placeholder page 0 into eval/pending.jsonl.

Usage:
  python eval\\park_pending.py            park unlabeled questions
  python eval\\park_pending.py --restore  put parked questions back
"""
import json
import sys

GOLDEN, PENDING = "eval/golden_set.jsonl", "eval/pending.jsonl"


def read(path):
    try:
        with open(path, encoding="utf-8-sig") as f:
            return [json.loads(line) for line in f if line.strip()]
    except FileNotFoundError:
        return []


def write(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


golden, pending = read(GOLDEN), read(PENDING)

if "--restore" in sys.argv:
    write(GOLDEN, golden + pending)
    write(PENDING, [])
    print(f"Restored {len(pending)} questions. golden_set now has {len(golden) + len(pending)}.")
else:
    keep = [q for q in golden if not any(r["page"] == 0 for r in q["relevant"])]
    parked = [q for q in golden if q not in keep]
    write(GOLDEN, keep)
    write(PENDING, pending + parked)
    print(f"Parked {len(parked)} unlabeled questions: {[q['id'] for q in parked]}")
    print(f"golden_set now has {len(keep)} questions.")