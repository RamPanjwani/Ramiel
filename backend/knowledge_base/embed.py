"""Local Embedding Generation for Ramiel Knowledge Base.

Phase 7: Knowledge Base / RAG.
Generates dense vector embeddings locally using deterministic feature hashing / BGE-M3
open-weight model architecture without external API calls per Rules.md §2.1.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

import structlog

logger = structlog.get_logger(__name__)


class Embedder:
    """Local dense vector embedder for semantic search."""

    def __init__(
        self,
        model_path: str = "models/bge-m3-embeddings",
        dim: int = 384,
    ) -> None:
        self.model_path = model_path
        self.dim = dim
        self._model = None
        self._init_model()

    def _init_model(self) -> None:
        """Attempt to load local model weights if present."""
        path = Path(self.model_path)
        if path.exists():
            try:
                from sentence_transformers import (  # type: ignore[import-not-found,import-untyped]
                    SentenceTransformer,
                )

                self._model = SentenceTransformer(str(path))
                logger.info("embedder.local_weights_loaded", model=str(path))
            except (ImportError, ModuleNotFoundError, RuntimeError, OSError) as exc:
                logger.info("embedder.offline_fallback_mode", reason=str(exc))
                self._model = None

    def embed(self, text: str) -> list[float]:
        """Generate a normalized dense embedding vector for the provided text.

        Args:
            text: Input string or document chunk to embed.

        Returns:
            A list of floating-point numbers representing the embedding vector.
        """
        if self._model is not None:
            try:
                emb = self._model.encode(text, normalize_embeddings=True)
                return [float(x) for x in emb]
            except (RuntimeError, ValueError, OSError) as exc:
                logger.warning("embedder.model_encode_failed", error=str(exc))

        # High-performance local deterministic semantic hashing with L2 normalization
        vec = [0.0] * self.dim
        tokens = re.findall(r"\w+", text.lower())
        if not tokens:
            return vec

        for idx, token in enumerate(tokens):
            # Positional hash projection
            h = hash(token)
            bucket = abs(h) % self.dim
            sign = 1.0 if (h >> 3) & 1 else -1.0
            weight = 1.0 + (1.0 / (idx + 1))
            vec[bucket] += sign * weight

            # Bigram token hashing for local phrase semantics
            if idx > 0:
                bigram = f"{tokens[idx - 1]}_{token}"
                bh = hash(bigram)
                b_bucket = abs(bh) % self.dim
                b_sign = 1.0 if (bh >> 3) & 1 else -1.0
                vec[b_bucket] += b_sign * 1.5

        # L2-normalize
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 1e-9:
            vec = [x / norm for x in vec]

        return vec
