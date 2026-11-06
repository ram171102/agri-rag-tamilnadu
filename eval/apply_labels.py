"""Apply page labels from eval/labels.txt to eval/golden_set.jsonl.

Line formats in labels.txt:
  q016: 123 124           pages in the question's placeholder document
  q031: cc22=60 cc21=62   explicit documents
  q028: same=q021         copy labels from an earlier question
  q027: none              no page answers it; question becomes unanswerable
"""
import json

DOCS = {
    "cpg": "tnau_cpg_agriculture_2020.pdf",
    "pn22": "tn_agri_policy_note_2022_23.pdf",
    "pn23": "tn_agri_policy_note_2023_24.pdf",
    "pn24": "tn_agri_policy_note_2024_25.pdf",
    "bs24": "tn_agri_budget_speech_2024_25.pdf",
    "cc21": "tn_agri_citizen_charter_2021_22.pdf",
    "cc22": "tn_agri_citizen_charter_2022_23.pdf",
}

valid = set()
with open("data/processed/chunks.jsonl", encoding="utf-8") as f:
    for line in f:
        c = json.loads(line)
        valid.add((c["doc"], c["page"]))

with open("eval/golden_set.jsonl", encoding="utf-8-sig") as f:
    questions = [json.loads(line) for line in f if line.strip()]
by_id = {q["id"]: q for q in questions}

errors = []
with open("eval/labels.txt", encoding="utf-8-sig") as f:
    for n, raw in enumerate(f, start=1):
        line = raw.split("#")[0].strip()
        if not line:
            continue
        qid, _, rest = line.partition(":")
        qid, tokens = qid.strip(), rest.split()
        q = by_id.get(qid)
        if q is None or not tokens:
            errors.append(f"labels.txt line {n}: bad question id or empty labels")
            continue
        if tokens == ["none"]:
            q["relevant"], q["type"] = [], "unanswerable"
            continue
        if len(tokens) == 1 and tokens[0].startswith("same="):
            src = by_id.get(tokens[0][5:])
            if src is None:
                errors.append(f"labels.txt line {n}: unknown source for {qid}")
            else:
                q["relevant"] = [dict(r) for r in src["relevant"]]
            continue
        placeholder = sorted({r["doc"] for r in q["relevant"]})
        rel = []
        for t in tokens:
            key, sep, page = t.partition("=")
            doc = DOCS.get(key) if sep else (placeholder[0] if len(placeholder) == 1 else None)
            page = page if sep else t
            if doc is None or not page.isdigit():
                errors.append(f"labels.txt line {n} ({qid}): cannot read '{t}'")
                continue
            if (doc, int(page)) not in valid:
                errors.append(f"labels.txt line {n} ({qid}): no chunks for {doc} p.{page}")
                continue
            rel.append({"doc": doc, "page": int(page)})
        q["relevant"] = rel

if errors:
    print("Nothing written. Fix these first:")
    for e in errors:
        print("  -", e)
else:
    with open("eval/golden_set.jsonl", "w", encoding="utf-8") as f:
        for q in questions:
            f.write(json.dumps(q, ensure_ascii=False) + "\n")
    left = sum(any(r["page"] == 0 for r in q["relevant"]) for q in questions)
    print(f"Golden set updated. Questions still at page 0: {left}")