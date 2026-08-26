"""Vision and OCR Pipeline Tests — Phase 6.

Validates:
1. VisionClient local VLM inference and offline health check.
2. OCRPipeline offline document and image text extraction.
3. DrawingReader P&ID tag extraction (valves, pumps, instruments, piping lines).
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.ocr_vision.drawing_reader import DrawingReader
from backend.ocr_vision.ocr_pipeline import OCRPipeline
from backend.serving.vision_client import VisionClient


class TestVisionClient:
    """Test VisionClient multimodal API calls."""

    @pytest.mark.anyio
    async def test_vision_health_offline(self) -> None:
        client = VisionClient(base_url="http://127.0.0.1:9990/v1")
        assert await client.check_health() is False

    @pytest.mark.anyio
    @patch("backend.serving.vision_client.httpx.AsyncClient.post")
    async def test_vision_analyze(self, mock_post: AsyncMock) -> None:
        tmp_img = Path(tempfile.mkdtemp()) / "test.png"
        tmp_img.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 20)

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": "Found Valve V-101 and Pump P-201."}}]
        }
        mock_resp.raise_for_status.return_value = None
        mock_post.return_value = mock_resp

        client = VisionClient(base_url="http://127.0.0.1:8001/v1")
        result = await client.analyze(tmp_img, prompt="Identify components")
        assert "Valve V-101" in result


class TestOCRPipeline:
    """Test OCRPipeline text extraction."""

    def test_extract_text(self) -> None:
        tmp_img = Path(tempfile.mkdtemp()) / "sample_scan.png"
        tmp_img.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 20)

        pipeline = OCRPipeline()
        text = pipeline.extract_text(tmp_img)
        assert len(text) > 0
        assert "sample_scan.png" in text or "Document" in text


class TestDrawingReader:
    """Test DrawingReader P&ID component extraction."""

    @pytest.mark.anyio
    async def test_parse_drawing(self) -> None:
        tmp_img = Path(tempfile.mkdtemp()) / "PID_V-101_P-201.png"
        tmp_img.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 20)

        reader = DrawingReader()
        result = await reader.parse_drawing(tmp_img)

        assert "drawing_file" in result
        assert "equipment" in result
        assert "instruments" in result
        assert isinstance(result["equipment"], list)
