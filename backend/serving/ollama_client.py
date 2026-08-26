"""Ollama Serving Client for Ramiel.

Phase 1: Single Model & Basic Chat.
Interfaces with a local Ollama serving daemon over loopback HTTP for lightweight
and fallback model inference.
"""

from __future__ import annotations

from pathlib import Path
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

    async def get_available_models(self) -> list[str]:
        """Fetch list of models available in local Ollama daemon."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    data = res.json()
                    return [m["name"] for m in data.get("models", [])]
        except (httpx.HTTPError, OSError):
            pass
        return []

    def _normalize_model_name(self, model: str, available_models: list[str]) -> str:
        """Resolve configured model path/id to the matching local Ollama model tag."""
        # 1. Clean path prefixes
        clean = Path(model).name.lower()
        clean = clean.replace("-7b", ":7b").replace("-8b", ":8b").replace("-14b", ":14b").replace("-32b", ":32b")

        # 2. Check direct match in available models
        for avail in available_models:
            avail_clean = avail.lower()
            if clean in avail_clean or avail_clean.split(":")[0] == clean.split(":")[0]:
                return avail

        # 3. If there is at least one model in Ollama and only one, use it as fallback
        if available_models and len(available_models) == 1:
            return available_models[0]

        return clean or model

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
        # Resolve best matching model tag from Ollama
        available = await self.get_available_models()
        target_model = self._normalize_model_name(model, available)

        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload: dict[str, Any] = {
            "model": target_model,
            "messages": messages,
            "stream": False,
        }
        if options:
            payload["options"] = options
        payload.update(kwargs)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            logger.debug("ollama.request", model=target_model, url=f"{self.base_url}/api/chat")
            res = await client.post(
                f"{self.base_url}/api/chat",
                json=payload,
            )
            res.raise_for_status()
            data = res.json()
            return str(data["message"]["content"])
