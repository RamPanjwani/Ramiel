"""Ollama Serving Client for Ramiel.

Phase 1: Single Model & Basic Chat.
Interfaces with a local Ollama serving daemon over loopback HTTP for lightweight
and fallback model inference.
"""

from __future__ import annotations

from typing import Any


class OllamaClient:
    """Client for local Ollama inference service."""

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:11434",
        timeout: float = 60.0,
    ) -> None:
        self.base_url = base_url
        self.timeout = timeout

    async def generate(self, prompt: str, **kwargs: Any) -> str:
        """Send a generation request to the local Ollama instance.

        Args:
            prompt: Text prompt to generate completion from.
            **kwargs: Additional inference parameters (temperature, model, options, etc.).

        Returns:
            The generated response string.

        Raises:
            NotImplementedError: Implementation pending Phase 1.
        """
        raise NotImplementedError("OllamaClient.generate is not yet implemented.")
