# Agri RAG: Tamil Nadu Farmer Knowledge Assistant

A citation-backed question-answering system over official Tamil Nadu
agriculture documents, with measured comparison of retrieval strategies.

## Problem

Information on crop management, pest control, fertilizer use, and
government schemes is scattered across long PDFs and multiple websites.
Finding an answer to a simple question such as "How do I control blast
disease in paddy?" takes time, and general-purpose chatbots may guess
incorrectly, which can lead to crop loss.

## Goal

Build a question-answering system over official agriculture documents that:

- Cites the source document and page for every answer
- Responds "Answer not found" instead of guessing when the documents
  do not contain the answer
- Supports queries in English and Tamil/Tanglish

## Approach

Compare three retrieval methods on the same evaluation set:

1. Naive embedding search (baseline)
2. Hybrid search (BM25 + embeddings)
3. Hybrid search + cross-encoder reranker

## Success Metrics

| Metric | Goal |
|---|---|
| Recall@5 | Improve over the naive baseline |
| Faithfulness | Answers supported by retrieved context |
| Unanswerable handling | Out-of-scope questions return "not found" |
| p95 latency | Under 3 seconds on CPU |

## Status

- [ ] Corpus collection
- [ ] Ingestion and chunking
- [ ] Naive baseline
- [ ] Golden evaluation set (50+ questions)
- [ ] Hybrid retrieval
- [ ] Reranker
- [ ] Faithfulness evaluation
- [ ] FastAPI, Docker, live demo

## Results

Coming soon.

## Limitations

To be updated during development.

## Disclaimer

This is a research project. Consult your local agriculture officer
before making crop decisions.