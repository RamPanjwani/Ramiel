"""Ollama Serving Client for Ramiel.

Phase 1: Single Model & Basic Chat.
Interfaces with a local Ollama serving daemon over loopback HTTP for lightweight
and fallback model inference.
"""

from __future__ import annotations

from typing import Any

import httpx
import structlog

logger = structlog.get_logger(__name__)


class OllamaClient:
    """Client for local Ollama inference service."""

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:11434",
        timeout: float = 60.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def check_health(self) -> bool:
        """Check if local Ollama daemon is reachable."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                return res.status_code == 200
        except (httpx.HTTPError, OSError):
            return False

    async def generate(
        self,
        prompt: str,
        model: str = "llama3-8b-instruct",
        system_prompt: str | None = None,
        options: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> str:
        """Send a generation request to the local Ollama instance.

        Args:
            prompt: Text prompt to generate completion from.
            model: Model name in Ollama local library.
            system_prompt: Optional system prompt.
            options: Model parameters (e.g. temperature, num_predict).
            **kwargs: Extra parameters.

        Returns:
            The generated response string.

        Raises:
            httpx.HTTPError: If Ollama fails or is unreachable.
        """
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": False,
        }
        if options:
            payload["options"] = options
        payload.update(kwargs)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            logger.debug("ollama.request", model=model, url=f"{self.base_url}/api/chat")
            res = await client.post(
                f"{self.base_url}/api/chat",
                json=payload,
            )
            res.raise_for_status()
            data = res.json()
            return str(data["message"]["content"])
