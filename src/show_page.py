"""Print all chunks of one or more pages of a document.

Usage:
  python src\\show_page.py tnau_cpg_agriculture_2020.pdf 282
  python src\\show_page.py tnau_cpg_agriculture_2020.pdf 282 283 285
  python src\\show_page.py tnau_cpg_agriculture_2020.pdf 282-285
  python src\\show_page.py tnau_cpg_agriculture_2020.pdf 282-285 290
"""
import json
import sys


def parse_pages(args):
    pages = []
    for a in args:
        if "-" in a:
            start, end = a.split("-")
            pages.extend(range(int(start), int(end) + 1))
        else:
            pages.append(int(a))
    return pages


doc = sys.argv[1]
wanted = parse_pages(sys.argv[2:])

by_page = {p: [] for p in wanted}
with open("data/processed/chunks.jsonl", encoding="utf-8") as f:
    for line in f:
        c = json.loads(line)
        if c["doc"] == doc and c["page"] in by_page:
            by_page[c["page"]].append(c["text"])

for page in wanted:
    print("=" * 70)
    print(f"{doc}  PAGE {page}")
    print("=" * 70)
    if by_page[page]:
        print("\n".join(by_page[page]))
    else:
        print("(no chunks for this page)")
    print()