"""Local Vector Store for Ramiel Knowledge Base.

Phase 7: Knowledge Base / RAG.
Manages vector indexing and similarity search using a local vector store
with SQLite persistence and exact cosine nearest-neighbor search.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two float vectors."""
    if len(a) != len(b) or not a:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b, strict=False))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(dot / (norm_a * norm_b))


class VectorStore:
    """Local vector store interface for semantic indexing and nearest-neighbor search."""

    def __init__(self, persist_dir: str | Path = "data/kb_index") -> None:
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.persist_dir / "vectors.db"
        self._init_db()

    def _init_db(self) -> None:
        """Initialize SQLite vector and metadata schema."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS document_chunks (
                    doc_id TEXT PRIMARY KEY,
                    text TEXT,
                    embedding_json TEXT,
                    metadata_json TEXT
                )
                """
            )
            conn.commit()

    def add(
        self,
        doc_id: str,
        embedding: list[float],
        text: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Add a document chunk and its embedding to the index."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO document_chunks (doc_id, text, embedding_json, metadata_json)
                VALUES (?, ?, ?, ?)
                """,
                (
                    doc_id,
                    text,
                    json.dumps(embedding),
                    json.dumps(metadata or {}),
                ),
            )
            conn.commit()

    def search(
        self, query_embedding: list[float], top_k: int = 5
    ) -> list[dict[str, Any]]:
        """Search the vector index for chunks most similar to the query embedding."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT doc_id, text, embedding_json, metadata_json FROM document_chunks"
            )
            rows = cursor.fetchall()

        scores: list[dict[str, Any]] = []
        for row in rows:
            doc_emb = json.loads(row["embedding_json"])
            score = cosine_similarity(query_embedding, doc_emb)
            scores.append(
                {
                    "doc_id": row["doc_id"],
                    "text": row["text"],
                    "score": score,
                    "metadata": json.loads(row["metadata_json"]),
                }
            )

        # Sort descending by cosine similarity
        scores.sort(key=lambda item: item["score"], reverse=True)
        return scores[:top_k]

    def count(self) -> int:
        """Return the number of indexed chunks."""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM document_chunks")
            return int(cursor.fetchone()[0])
