"""Hybrid Search for Ramiel Knowledge Base.

Phase 7: Knowledge Base / RAG.
Combines dense vector similarity search with BM25 / term-matching retrieval
and rank fusion to achieve high recall and precise technical term matching.
"""

from __future__ import annotations

import math
import re
from typing import Any

from backend.knowledge_base.embed import Embedder
from backend.knowledge_base.vector_store import VectorStore


def compute_bm25_score(
    query_tokens: list[str],
    doc_tokens: list[str],
    avg_len: float = 100.0,
    k1: float = 1.5,
    b: float = 0.75,
) -> float:
    """Compute local BM25 relevance score for a document."""
    if not query_tokens or not doc_tokens:
        return 0.0

    doc_len = len(doc_tokens)
    tf_counts: dict[str, int] = {}
    for t in doc_tokens:
        tf_counts[t] = tf_counts.get(t, 0) + 1

    score = 0.0
    for q in query_tokens:
        if q in tf_counts:
            tf = tf_counts[q]
            idf = math.log(1.0 + (100.0 / (1.0 + 1.0)))  # Smooth IDF
            numerator = tf * (k1 + 1.0)
            denominator = tf + k1 * (1.0 - b + b * (doc_len / max(avg_len, 1.0)))
            score += idf * (numerator / max(denominator, 1e-9))
    return float(score)


class HybridSearch:
    """Combines semantic vector search with BM25 keyword retrieval."""

    def __init__(
        self,
        vector_store: VectorStore | None = None,
        embedder: Embedder | None = None,
        vector_weight: float = 0.7,
        keyword_weight: float = 0.3,
    ) -> None:
        self.vector_store = vector_store or VectorStore()
        self.embedder = embedder or Embedder()
        self.vector_weight = vector_weight
        self.keyword_weight = keyword_weight

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Perform hybrid search over the knowledge base combining vector and keyword signals."""
        if not query.strip():
            return []

        # 1. Semantic Vector Retrieval
        query_emb = self.embedder.embed(query)
        vector_results = self.vector_store.search(query_emb, top_k=top_k * 2)

        # 2. Keyword & BM25 Scoring
        query_tokens = re.findall(r"\w+", query.lower())
        hybrid_ranked: list[dict[str, Any]] = []

        for item in vector_results:
            doc_text = item.get("text", "")
            doc_tokens = re.findall(r"\w+", doc_text.lower())
            bm25_val = compute_bm25_score(query_tokens, doc_tokens)

            # Normalize BM25 approximately into [0, 1] range
            normalized_bm25 = min(1.0, bm25_val / 10.0) if bm25_val > 0 else 0.0
            vector_score = max(0.0, item["score"])

            # Weighted Hybrid Fusion Score
            final_score = (self.vector_weight * vector_score) + (
                self.keyword_weight * normalized_bm25
            )

            hybrid_ranked.append(
                {
                    "doc_id": item["doc_id"],
                    "text": doc_text,
                    "score": round(final_score, 4),
                    "vector_score": round(vector_score, 4),
                    "bm25_score": round(normalized_bm25, 4),
                    "metadata": item.get("metadata", {}),
                }
            )

        # Rank descending
        hybrid_ranked.sort(key=lambda x: x["score"], reverse=True)
        return hybrid_ranked[:top_k]
