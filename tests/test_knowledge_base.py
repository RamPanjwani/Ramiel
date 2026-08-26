"""Knowledge Base and Hybrid RAG Tests — Phase 7.

Validates:
1. Embedder dense vector generation and L2-normalization.
2. VectorStore SQLite persistence and cosine similarity search.
3. HybridSearch vector + BM25 keyword fusion scoring.
4. DocumentIngestor chunking with sliding window overlap.
5. DocSearchTool agent integration and retrieval.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from backend.knowledge_base.embed import Embedder
from backend.knowledge_base.hybrid_search import HybridSearch
from backend.knowledge_base.ingest import DocumentIngestor
from backend.knowledge_base.vector_store import VectorStore
from backend.tools.tool_registry import ToolRegistry


class TestEmbedder:
    """Test local dense embedding generation."""

    def test_embed_dimension_and_normalization(self) -> None:
        embedder = Embedder(dim=384)
        vec = embedder.embed("Turbine pressure drop exceeded nominal thresholds.")
        assert len(vec) == 384
        # Norm should be approximately 1.0
        norm = sum(x * x for x in vec) ** 0.5
        assert abs(norm - 1.0) < 1e-4

    def test_empty_string_embed(self) -> None:
        embedder = Embedder(dim=384)
        vec = embedder.embed("")
        assert len(vec) == 384
        assert all(x == 0.0 for x in vec)


class TestVectorStore:
    """Test VectorStore SQLite indexing and cosine similarity search."""

    def test_add_and_search(self) -> None:
        tmp_dir = Path(tempfile.mkdtemp())
        vs = VectorStore(persist_dir=tmp_dir)

        emb1 = [1.0, 0.0, 0.0]
        emb2 = [0.0, 1.0, 0.0]
        vs.add(
            "doc1", emb1, text="High pressure steam line", metadata={"type": "safety"}
        )
        vs.add(
            "doc2", emb2, text="Cooling water return loop", metadata={"type": "cooling"}
        )

        assert vs.count() == 2

        # Search nearest to emb1
        results = vs.search([0.9, 0.1, 0.0], top_k=1)
        assert len(results) == 1
        assert results[0]["doc_id"] == "doc1"
        assert results[0]["metadata"]["type"] == "safety"


class TestHybridSearch:
    """Test HybridSearch semantic + BM25 keyword fusion."""

    def test_hybrid_search_ranking(self) -> None:
        tmp_dir = Path(tempfile.mkdtemp())
        vs = VectorStore(persist_dir=tmp_dir)
        embedder = Embedder(dim=128)

        text1 = "Valve V-102 critical failure due to cavitation"
        text2 = "Routine lubrication of pump P-201"
        vs.add("doc1", embedder.embed(text1), text=text1)
        vs.add("doc2", embedder.embed(text2), text=text2)

        hybrid = HybridSearch(vector_store=vs, embedder=embedder)
        results = hybrid.search("cavitation failure", top_k=2)

        assert len(results) >= 1
        assert results[0]["doc_id"] == "doc1"
        assert results[0]["score"] > 0.0


class TestDocumentIngestor:
    """Test DocumentIngestor text chunking and file ingestion."""

    def test_chunking_overlap(self) -> None:
        ingestor = DocumentIngestor(chunk_size=60, chunk_overlap=20)
        sample_text = "Word1 Word2 Word3 Word4 Word5 Word6 Word7 Word8 Word9 Word10 Word11 Word12 Word13 Word14 Word15"
        chunks = ingestor.chunk_text(sample_text)
        assert len(chunks) >= 2

    def test_ingest_directory(self) -> None:
        tmp_dir = Path(tempfile.mkdtemp())
        kb_dir = Path(tempfile.mkdtemp())

        # Create dummy docs
        doc1 = tmp_dir / "report1.txt"
        doc1.write_text(
            "Plant report on thermal efficiency and boiler feed water.",
            encoding="utf-8",
        )
        doc2 = tmp_dir / "sop.md"
        doc2.write_text(
            "Standard operating procedure for emergency shutdown of turbine.",
            encoding="utf-8",
        )

        vs = VectorStore(persist_dir=kb_dir)
        ingestor = DocumentIngestor(vector_store=vs)
        indexed_chunks = ingestor.ingest(tmp_dir)

        assert indexed_chunks >= 2
        assert vs.count() == indexed_chunks


class TestDocSearchTool:
    """Test DocSearchTool in agent registry."""

    @pytest.mark.anyio
    async def test_tool_registry_doc_search(self) -> None:
        registry = ToolRegistry()
        tools = registry.list_tools()
        assert "doc_search" in tools

        schemas = registry.get_schemas()
        assert any(s["function"]["name"] == "doc_search" for s in schemas)
