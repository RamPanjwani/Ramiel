"""Document Search Tool for Ramiel.

Phase 7: Knowledge Base / RAG.
Interfaces with local knowledge base indexes (hybrid vector + BM25) to provide
grounded document chunks and citations to the agent orchestrator.
"""

from __future__ import annotations

from typing import Any

from backend.knowledge_base.hybrid_search import HybridSearch


class DocSearchTool:
    """Agent tool for semantic and keyword retrieval over local enterprise documents."""

    def __init__(self, hybrid_search: HybridSearch | None = None) -> None:
        self.hybrid_search = hybrid_search or HybridSearch()

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Search the local knowledge base for relevant document passages.

        Args:
            query: Natural language query or keywords.
            top_k: Maximum number of relevant document chunks to return.

        Returns:
            A list of search result dictionaries containing content, source document ID,
            scores, and metadata citations.
        """
        return self.hybrid_search.search(query=query, top_k=top_k)
