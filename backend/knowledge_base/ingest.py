"""Document Ingestion for Ramiel Knowledge Base.

Phase 7: Knowledge Base / RAG.
Loads enterprise documents (PDFs, SOPs, manuals, reports), chunks text with
structural awareness, extracts metadata, and triggers embedding and indexing.
"""

from __future__ import annotations

import re
import uuid
from pathlib import Path

import structlog

from backend.knowledge_base.embed import Embedder
from backend.knowledge_base.vector_store import VectorStore

logger = structlog.get_logger(__name__)


class DocumentIngestor:
    """Ingests, chunks, and processes raw documents into knowledge base records."""

    def __init__(
        self,
        vector_store: VectorStore | None = None,
        embedder: Embedder | None = None,
        chunk_size: int = 512,
        chunk_overlap: int = 64,
    ) -> None:
        self.vector_store = vector_store or VectorStore()
        self.embedder = embedder or Embedder()
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str) -> list[str]:
        """Split text into overlapping character/word chunks."""
        words = re.findall(r"\S+", text)
        if not words:
            return []

        chunks: list[str] = []
        words_per_chunk = max(1, self.chunk_size // 6)  # Approx 6 chars/word
        overlap_words = max(0, self.chunk_overlap // 6)

        step = max(1, words_per_chunk - overlap_words)
        for i in range(0, len(words), step):
            chunk_words = words[i : i + words_per_chunk]
            chunks.append(" ".join(chunk_words))
            if i + words_per_chunk >= len(words):
                break
        return chunks

    def ingest_file(self, file_path: str | Path) -> int:
        """Ingest a single document file, creating and indexing chunks."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Source file not found: {path}")

        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError as exc:
            logger.warning("ingest.read_failed", file=str(path), error=str(exc))
            return 0

        chunks = self.chunk_text(content)
        for idx, chunk in enumerate(chunks):
            doc_id = f"{path.stem}_{idx}_{uuid.uuid4().hex[:4]}"
            embedding = self.embedder.embed(chunk)
            metadata = {
                "source_file": str(path),
                "filename": path.name,
                "chunk_index": idx,
                "total_chunks": len(chunks),
            }
            self.vector_store.add(
                doc_id=doc_id, embedding=embedding, text=chunk, metadata=metadata
            )

        logger.info("ingest.file_completed", file=path.name, chunks=len(chunks))
        return len(chunks)

    def ingest(self, path: str | Path) -> int:
        """Ingest a file or directory of documents, creating indexed chunks."""
        target = Path(path)
        if not target.exists():
            raise FileNotFoundError(f"Target path not found: {target}")

        if target.is_file():
            return self.ingest_file(target)

        total_chunks = 0
        for item in target.glob("**/*"):
            if item.is_file() and item.suffix.lower() in {
                ".txt",
                ".md",
                ".csv",
                ".json",
                ".py",
                ".yaml",
                ".yml",
            }:
                total_chunks += self.ingest_file(item)

        logger.info(
            "ingest.directory_completed", dir=str(target), total_chunks=total_chunks
        )
        return total_chunks
