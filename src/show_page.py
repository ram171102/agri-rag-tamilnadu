"""Print all chunks of one page.

Usage: python src\\show_page.py tn_agri_citizen_charter_2021_22.pdf 45
"""
import json
import sys

doc, page = sys.argv[1], int(sys.argv[2])
with open("data/processed/chunks.jsonl", encoding="utf-8") as f:
    for line in f:
        c = json.loads(line)
        if c["doc"] == doc and c["page"] == page:
            print(c["text"])
            print()