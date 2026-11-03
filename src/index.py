"""Embed all chunks and save the vectors to disk."""
import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

CHUNKS = Path("data/processed/chunks.jsonl")
EMB = Path("data/processed/embeddings.npy")
MODEL = "BAAI/bge-small-en-v1.5"


def main():
    with open(CHUNKS, encoding="utf-8") as f:
        texts = [json.loads(line)["text"] for line in f]
    print(f"Embedding {len(texts)} chunks with {MODEL}")
    model = SentenceTransformer(MODEL)
    emb = model.encode(
        texts, batch_size=32, normalize_embeddings=True, show_progress_bar=True
    )
    np.save(EMB, emb.astype("float32"))
    print(f"Saved {emb.shape} -> {EMB}")


if __name__ == "__main__":
    main()