"""Write candidate pages for every unlabeled golden-set question.

Keyword overlap only (no embeddings), weighted so rare words count more, and
restricted to the document(s) named in the question's placeholder label.
Usage: python eval\\label_worksheet.py   ->  eval/worksheet.txt
"""
import json
import math
import re
from collections import defaultdict

STOP = {
    "the", "and", "for", "what", "which", "who", "how", "when", "where", "are",
    "is", "of", "in", "on", "to", "by", "with", "under", "from", "does", "do",
    "did", "between", "should", "needed", "given", "available", "recommended",
    "required", "optimum",
}
SKIP = {"q028", "q029", "q030"}  # Tanglish copies: label them with same=...
TOP = 6

pages = defaultdict(str)
with open("data/processed/chunks.jsonl", encoding="utf-8") as f:
    for line in f:
        c = json.loads(line)
        pages[(c["doc"], c["page"])] += " " + c["text"].lower()

with open("eval/golden_set.jsonl", encoding="utf-8-sig") as f:
    questions = [json.loads(line) for line in f if line.strip()]

N = len(pages)
lines = []
for q in questions:
    docs = sorted({r["doc"] for r in q["relevant"] if r["page"] == 0})
    if q["id"] in SKIP or not docs:
        continue
    words = [w for w in re.findall(r"[a-z0-9]+", q["question"].lower())
             if w not in STOP and len(w) > 2]
    stems = sorted({w[:6] for w in words})  # crude stemming
    idf = {s: math.log((N + 1) / (sum(s in t for t in pages.values()) + 1)) for s in stems}

    lines += ["=" * 78, f"{q['id']}  {q['question']}", f"keywords: {stems}"]
    for doc in docs:
        scored = []
        for (d, p), t in pages.items():
            if d == doc:
                present = [s for s in stems if s in t]
                if present:
                    scored.append((sum(idf[s] for s in present), p, present, t))
        scored.sort(key=lambda x: -x[0])
        lines.append(f"-- {doc}")
        for score, p, present, t in scored[:TOP]:
            best = max(present, key=lambda s: idf[s])
            i = t.find(best)
            snip = t[max(0, i - 90): i + 130]
            lines.append(f"  p.{p:<4} score {score:5.1f}  matched {len(present)}/{len(stems)}  ...{snip}...")
    lines.append("")

with open("eval/worksheet.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("wrote eval/worksheet.txt")