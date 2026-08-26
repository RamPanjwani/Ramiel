"""vLLM Serving Client for Ramiel.

Phase 1: Single Model & Basic Chat.
Interfaces with a local vLLM serving instance over loopback HTTP/IPC for high-throughput,
GPU-accelerated local inference.
"""

from __future__ import annotations

from typing import Any

import httpx
import structlog

logger = structlog.get_logger(__name__)


class VLLMClient:
    """Client for local vLLM inference engine (OpenAI-compatible local API)."""

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8001/v1",
        timeout: float = 60.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def check_health(self) -> bool:
        """Check if local vLLM server is reachable."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(f"{self.base_url}/models")
                return res.status_code == 200
        except (httpx.HTTPError, OSError):
            return False

    async def generate(
        self,
        prompt: str,
        model: str = "llama3-8b-instruct",
        temperature: float = 0.2,
        max_tokens: int = 2048,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Send a chat completion request to the local vLLM instance.

        Args:
            prompt: Text prompt to generate completion from.
            model: Model name/path served by vLLM.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.
            system_prompt: Optional system instructions.
            **kwargs: Extra parameters passed to the completion API.

        Returns:
            The generated response string.

        Raises:
            httpx.HTTPError: If the server returns an error or is unreachable.
        """
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs,
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            logger.debug("vllm.request", model=model, url=f"{self.base_url}/chat/completions")
            res = await client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
            )
            res.raise_for_status()
            data = res.json()
            return str(data["choices"][0]["message"]["content"])
