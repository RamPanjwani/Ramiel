"""Vision Serving Client for Ramiel.

Phase 6: Multimodal (OCR + Vision).
Interfaces with a local Vision-Language Model (e.g. Qwen2-VL) serving endpoint
to analyze technical drawings, scanned documents, and images locally.
"""

from __future__ import annotations

import base64
from pathlib import Path
from typing import Any

import httpx
import structlog

logger = structlog.get_logger(__name__)


class VisionClient:
    """Client for local Vision-Language Model inference (OpenAI-compatible multimodal API)."""

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8001/v1",
        timeout: float = 120.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def check_health(self) -> bool:
        """Check if local vision server is reachable."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(f"{self.base_url}/models")
                return res.status_code == 200
        except (httpx.HTTPError, OSError):
            return False

    async def analyze(
        self,
        image_path: str | Path,
        prompt: str = "Analyze this technical drawing and extract all equipment tags, instruments, and connections.",
        model: str = "qwen2-vl-7b",
        **kwargs: Any,
    ) -> str:
        """Analyze an image or visual artifact using a local vision model.

        Args:
            image_path: Path to the image file on local disk.
            prompt: Text prompt/question guiding the visual analysis.
            model: Model name / identifier configured in model_registry.yaml.
            **kwargs: Additional inference parameters.

        Returns:
            The textual analysis or structured description produced by the model.
        """
        img_file = Path(image_path)
        if not img_file.exists():
            raise FileNotFoundError(f"Image file not found: {img_file}")

        # Base64 encode image
        image_bytes = img_file.read_bytes()
        b64_str = base64.b64encode(image_bytes).decode("utf-8")
        media_type = "image/png" if img_file.suffix.lower() == ".png" else "image/jpeg"

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{media_type};base64,{b64_str}"},
                    },
                ],
            }
        ]

        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", 2048),
            "temperature": kwargs.get("temperature", 0.1),
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            logger.debug("vision.request", model=model, image=str(img_file))
            res = await client.post(f"{self.base_url}/chat/completions", json=payload)
            res.raise_for_status()
            data = res.json()
            return str(data["choices"][0]["message"]["content"])
