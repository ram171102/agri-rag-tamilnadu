"""Ingest PDFs into page-aware text chunks (JSONL).

Each chunk keeps its source document, year, and page number so answers
can be cited later.
"""
import csv
import json
import re
from collections import Counter
from pathlib import Path

import pymupdf  # PyMuPDF

RAW = Path("data/raw")
OUT = Path("data/processed/chunks.jsonl")
SOURCES = Path("data/sources.csv")

CHUNK_WORDS = 350
OVERLAP = 50
MIN_WORDS = 40
MAX_NON_ASCII = 0.2  # pages above this are likely garbled Tamil text


def load_sources():
    with open(SOURCES, encoding="utf-8-sig", newline="") as f:
        return {row["file"]: row for row in csv.DictReader(f)}


def page_lines(doc):
    return [
        [ln.strip() for ln in page.get_text().splitlines() if ln.strip()]
        for page in doc
    ]


def repeated_lines(pages, threshold=0.3):
    """Lines that repeat on many pages are headers/footers."""
    n = len(pages)
    if n < 5:
        return set()
    counts = Counter(ln for lines in pages for ln in set(lines))
    return {ln for ln, c in counts.items() if c / n >= threshold and len(ln) < 80}


def chunk_words(text, size=CHUNK_WORDS, overlap=OVERLAP):
    words = text.split()
    step = size - overlap
    for i in range(0, len(words), step):
        piece = words[i : i + size]
        if len(piece) >= MIN_WORDS:
            yield " ".join(piece)


def ingest():
    sources = load_sources()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    total = 0
    with open(OUT, "w", encoding="utf-8") as out:
        for pdf in sorted(RAW.glob("*.pdf")):
            meta = sources.get(pdf.name)
            if meta is None:
                print(f"SKIP  {pdf.name}: not listed in sources.csv")
                continue

            doc = pymupdf.open(pdf)
            pages = page_lines(doc)
            boiler = repeated_lines(pages)
            empty = garbled = n_chunks = 0

            for page_no, lines in enumerate(pages, start=1):
                lines = [
                    ln for ln in lines
                    if ln not in boiler and not re.fullmatch(r"\d{1,4}", ln)
                ]
                text = re.sub(r"\s+", " ", " ".join(lines)).strip()
                if not text:
                    empty += 1
                    continue
                if sum(ord(c) > 127 for c in text) / len(text) > MAX_NON_ASCII:
                    garbled += 1
                    continue
                for j, chunk in enumerate(chunk_words(text)):
                    rec = {
                        "chunk_id": f"{pdf.stem}-p{page_no}-{j}",
                        "doc": pdf.name,
                        "title": meta["title"],
                        "year": int(meta["year"]),
                        "page": page_no,
                        "text": chunk,
                    }
                    out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    n_chunks += 1

            total += n_chunks
            print(f"{pdf.name}: {len(pages)} pages, {n_chunks} chunks, "
                  f"{empty} empty, {garbled} garbled, "
                  f"{len(boiler)} header/footer lines removed")
    print(f"\nTotal chunks: {total} -> {OUT}")


if __name__ == "__main__":
    ingest()