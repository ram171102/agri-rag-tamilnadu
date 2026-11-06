"""Reword questions whose original wording does not match the source documents.

Run once, before apply_labels.py:
    python eval\\revise_questions.py
"""
import json

NEW_TEXT = {
    # The guide never says "rabi"; it uses Tamil season names (Puratasi = Sep-Oct).
    "q022": "Which sorghum varieties are recommended for the Puratasi (September-October) season?",
    # "Area expansion of banana" has no single heading; the amounts are per-hectare planting subsidies.
    "q036": "What subsidy is given for planting tissue culture banana?",
}

with open("eval/golden_set.jsonl", encoding="utf-8-sig") as f:
    rows = [json.loads(line) for line in f if line.strip()]

changed = []
for q in rows:
    if q["id"] in NEW_TEXT:
        q["question"] = NEW_TEXT[q["id"]]
        changed.append(q["id"])

with open("eval/golden_set.jsonl", "w", encoding="utf-8") as f:
    for q in rows:
        f.write(json.dumps(q, ensure_ascii=False) + "\n")

print("Reworded:", changed)