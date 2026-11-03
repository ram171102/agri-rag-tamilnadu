"""Evaluate retrieval against the golden set.

Usage: python eval\run_retrieval_eval.py [--method naive] [--k 5]

Relevance is judged at (document, page) level, so the eval keeps working if
chunking changes later. Retrieved chunks are collapsed to unique pages in
rank order before scoring.
"""
import argparse
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.retrieve import HybridRetriever, NaiveRetriever  # noqa: E402  # noqa: E402

GOLDEN = ROOT / "eval" / "golden_set.jsonl"
CHUNKS = ROOT / "data" / "processed" / "chunks.jsonl"
RESULTS = ROOT / "eval" / "results"
METHODS = {"naive": NaiveRetriever, "hybrid": HybridRetriever}


def load_pages():
    pages = set()
    with open(CHUNKS, encoding="utf-8") as f:
        for line in f:
            c = json.loads(line)
            pages.add((c["doc"], c["page"]))
    return pages


def load_golden(valid_pages):
    questions, errors = [], []
    with open(GOLDEN, encoding="utf-8-sig") as f:
        for n, line in enumerate(f, start=1):
            if not line.strip():
                continue
            try:
                q = json.loads(line)
            except json.JSONDecodeError as e:
                errors.append(f"line {n}: invalid JSON ({e})")
                continue
            missing = [x for x in ("id", "question", "type", "relevant") if x not in q]
            if missing:
                errors.append(f"line {n}: missing {missing}")
                continue
            for r in q["relevant"]:
                if (r.get("doc"), r.get("page")) not in valid_pages:
                    errors.append(f"line {n} ({q['id']}): no chunks for {r}")
            q.setdefault("lang", "en")
            questions.append(q)
    return questions, errors


def ranked_pages(hits):
    seen, out = set(), []
    for h in hits:
        key = (h["doc"], h["page"])
        if key not in seen:
            seen.add(key)
            out.append(key)
    return out


def run(method, k):
    retriever = METHODS[method]()
    questions, errors = load_golden(load_pages())
    if errors:
        print("Fix these golden-set problems first:")
        for e in errors:
            print("  -", e)
        sys.exit(1)

    rows = []
    for q in questions:
        hits = retriever.search(q["question"], k=30)
        pages = ranked_pages(hits)[:k]
        row = {
            "id": q["id"],
            "question": q["question"],
            "type": q["type"],
            "lang": q["lang"],
            "top_score": hits[0]["score"],
            "retrieved": [list(p) for p in pages],
        }
        rel = {(r["doc"], r["page"]) for r in q["relevant"]}
        if rel:
            found = rel & set(pages)
            rank = next((i for i, p in enumerate(pages, 1) if p in rel), None)
            row.update(
                hit=bool(found),
                recall=len(found) / len(rel),
                rr=1 / rank if rank else 0.0,
                expected=[list(p) for p in sorted(rel)],
            )
        rows.append(row)
    return rows


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else float("nan")


def summarize(rows, k):
    ans = [r for r in rows if "hit" in r]
    unans = [r for r in rows if "hit" not in r]
    print(f"\n=== {len(ans)} answerable, {len(unans)} unanswerable questions ===")
    print(f"Hit@{k}     {mean(float(r['hit']) for r in ans):.2f}   (any relevant page in top {k})")
    print(f"Recall@{k}  {mean(r['recall'] for r in ans):.2f}   (share of relevant pages found)")
    print(f"MRR@{k}     {mean(r['rr'] for r in ans):.2f}")

    for key in ("type", "lang"):
        groups = defaultdict(list)
        for r in ans:
            groups[r[key]].append(r)
        print()
        for name, rs in sorted(groups.items()):
            print(f"  {key}={name:<10} n={len(rs):<3} "
                  f"Hit@{k}={mean(float(r['hit']) for r in rs):.2f}  "
                  f"MRR={mean(r['rr'] for r in rs):.2f}")

    if ans:
        a = sorted(r["top_score"] for r in ans)
        print(f"\nTop-1 score, answerable:   min {a[0]:.3f}  "
              f"median {statistics.median(a):.3f}  max {a[-1]:.3f}")
    if unans:
        u = sorted(r["top_score"] for r in unans)
        print(f"Top-1 score, unanswerable: min {u[0]:.3f}  "
              f"median {statistics.median(u):.3f}  max {u[-1]:.3f}")
        print("If these ranges overlap, a plain score threshold cannot separate them.")

    misses = [r for r in ans if not r["hit"]]
    if misses:
        print(f"\nMissed ({len(misses)}):")
        for r in misses:
            print(f"  {r['id']}  {r['question']}")
            print(f"      expected: {r['expected']}")
            print(f"      got:      {r['retrieved'][:3]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--method", default="naive", choices=METHODS)
    ap.add_argument("--k", type=int, default=5)
    args = ap.parse_args()

    rows = run(args.method, args.k)
    summarize(rows, args.k)

    RESULTS.mkdir(parents=True, exist_ok=True)
    out = RESULTS / f"{args.method}.json"
    out.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"\nSaved per-question results -> {out}")


if __name__ == "__main__":
    main()