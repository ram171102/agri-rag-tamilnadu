"""Retrievers: naive dense, and hybrid (dense + BM25 with RRF fusion).

Usage: python src\\retrieve.py [--hybrid] "your question"
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

CHUNKS = Path("data/processed/chunks.jsonl")
EMB = Path("data/processed/embeddings.npy")
MODEL = "BAAI/bge-small-en-v1.5"
# bge models work best with this prefix on the query side only
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "of", "in", "on", "for", "to",
    "and", "or", "how", "what", "which", "who", "when", "where", "does", "do",
    "be", "by", "with", "under", "from", "at", "as", "it", "this", "that",
}


def tokenize(text):
    return [t for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in STOPWORDS]


class NaiveRetriever:
    def __init__(self):
        with open(CHUNKS, encoding="utf-8") as f:
            self.chunks = [json.loads(line) for line in f]
        self.emb = np.load(EMB)
        self.model = SentenceTransformer(MODEL)

    def _dense_scores(self, query):
        q = self.model.encode([QUERY_PREFIX + query], normalize_embeddings=True)[0]
        return self.emb @ q  # cosine similarity (vectors are normalized)

    def search(self, query, k=5):
        scores = self._dense_scores(query)
        top = np.argsort(-scores)[:k]
        return [{**self.chunks[i], "score": float(scores[i])} for i in top]


class HybridRetriever(NaiveRetriever):
    """Dense + BM25, fused with Reciprocal Rank Fusion.

    "score" stays the dense cosine of each chunk (comparable with the naive
    retriever); "rrf" is the fused score used for ranking.
    """

    def __init__(self, pool=50, rrf_k=60):
        super().__init__()
        self.bm25 = BM25Okapi([tokenize(c["text"]) for c in self.chunks])
        self.pool = pool
        self.rrf_k = rrf_k

    def search(self, query, k=5):
        dense = self._dense_scores(query)
        sparse = self.bm25.get_scores(tokenize(query))

        rankings = [np.argsort(-dense)[: self.pool]]
        if sparse.max() > 0:  # skip BM25 if no query term appears anywhere
            rankings.append(np.argsort(-sparse)[: self.pool])

        fused = {}
        for ranking in rankings:
            for rank, i in enumerate(ranking, start=1):
                fused[i] = fused.get(i, 0.0) + 1.0 / (self.rrf_k + rank)

        top = sorted(fused, key=fused.get, reverse=True)[:k]
        return [
            {**self.chunks[i], "score": float(dense[i]), "rrf": fused[i]}
            for i in top
        ]


if __name__ == "__main__":
    args = sys.argv[1:]
    hybrid = "--hybrid" in args
    query = " ".join(a for a in args if a != "--hybrid")
    retriever = HybridRetriever() if hybrid else NaiveRetriever()
    for rank, hit in enumerate(retriever.search(query), start=1):
        extra = f"  rrf={hit['rrf']:.4f}" if "rrf" in hit else ""
        print(f"\n#{rank}  cosine={hit['score']:.3f}{extra}  {hit['doc']}  p.{hit['page']}")
        print(hit["text"][:300].replace("\n", " "), "...")