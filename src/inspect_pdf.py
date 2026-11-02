"""List pages with little or no text, with a short preview."""
import sys

import pymupdf

MIN_WORDS = 40

doc = pymupdf.open(sys.argv[1])
for i, page in enumerate(doc, start=1):
    text = " ".join(page.get_text().split())
    n = len(text.split())
    if n < MIN_WORDS:
        print(f"page {i}: {n} words | {text[:70]!r}")