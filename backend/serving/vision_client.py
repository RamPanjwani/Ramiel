"""Vision Serving Client for Ramiel.

Phase 6: Multimodal (OCR + Vision).
Interfaces with a local Vision-Language Model (e.g. Qwen2-VL) serving endpoint
to analyze technical drawings, scanned documents, and images locally.
"""

from __future__ import annotations

from typing import Any


class VisionClient:
    """Client for local Vision-Language Model inference."""

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8000/v1",
        timeout: float = 120.0,
    ) -> None:
        self.base_url = base_url
        self.timeout = timeout

    async def analyze(self, image_path: str, prompt: str, **kwargs: Any) -> str:
        """Analyze an image or visual artifact using a local vision model.

        Args:
            image_path: Path to the image file on local disk.
            prompt: Text prompt/question guiding the visual analysis.
            **kwargs: Additional inference parameters.

        Returns:
            The textual analysis or structured description produced by the model.

        Raises:
            NotImplementedError: Implementation pending Phase 6.
        """
        raise NotImplementedError("VisionClient.analyze is not yet implemented.")
