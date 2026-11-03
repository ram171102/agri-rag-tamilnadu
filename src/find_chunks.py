"""Keyword search over chunks.jsonl, independent of embeddings.

Used to label relevant pages for the golden eval set.
Usage: python src\find_chunks.py blast paddy   (all terms must appear)
"""
import json
import sys

terms = [t.lower() for t in sys.argv[1:]]
found = 0
with open("data/processed/chunks.jsonl", encoding="utf-8") as f:
    for line in f:
        chunk = json.loads(line)
        text = chunk["text"].lower()
        if all(t in text for t in terms):
            found += 1
            i = text.find(terms[0])
            snippet = chunk["text"][max(0, i - 60): i + 140]
            print(f"{chunk['doc']}  p.{chunk['page']}\n   ...{snippet}...\n")
print(f"{found} matching chunks")