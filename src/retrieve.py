"""Naive dense retrieval: embed the query, return the closest chunks."""
import json
import sys
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

CHUNKS = Path("data/processed/chunks.jsonl")
EMB = Path("data/processed/embeddings.npy")
MODEL = "BAAI/bge-small-en-v1.5"
# bge models work best with this prefix on the query side only
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "


class NaiveRetriever:
    def __init__(self):
        with open(CHUNKS, encoding="utf-8") as f:
            self.chunks = [json.loads(line) for line in f]
        self.emb = np.load(EMB)
        self.model = SentenceTransformer(MODEL)

    def search(self, query, k=5):
        q = self.model.encode([QUERY_PREFIX + query], normalize_embeddings=True)[0]
        scores = self.emb @ q  # cosine similarity (vectors are normalized)
        top = np.argsort(-scores)[:k]
        return [{**self.chunks[i], "score": float(scores[i])} for i in top]


if __name__ == "__main__":
    query = " ".join(sys.argv[1:])
    for rank, hit in enumerate(NaiveRetriever().search(query), start=1):
        print(f"\n#{rank}  score={hit['score']:.3f}  {hit['doc']}  p.{hit['page']}")
        print(hit["text"][:300].replace("\n", " "), "...")