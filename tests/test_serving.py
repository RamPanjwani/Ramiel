"""Unit tests for local model serving clients (Phase 1)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.serving.ollama_client import OllamaClient
from backend.serving.vllm_client import VLLMClient


class TestVLLMClient:
    """Test vLLM local client integration."""

    @pytest.mark.anyio
    async def test_health_check_offline(self) -> None:
        client = VLLMClient(base_url="http://127.0.0.1:9999/v1")
        is_healthy = await client.check_health()
        assert is_healthy is False

    @pytest.mark.anyio
    @patch("backend.serving.vllm_client.httpx.AsyncClient.post")
    async def test_generate_success(self, mock_post: AsyncMock) -> None:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Sample model response from vLLM"}}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        client = VLLMClient(base_url="http://127.0.0.1:8001/v1")
        result = await client.generate(prompt="What is sovereignty?")
        assert result == "Sample model response from vLLM"


class TestOllamaClient:
    """Test Ollama local client integration."""

    @pytest.mark.anyio
    async def test_health_check_offline(self) -> None:
        client = OllamaClient(base_url="http://127.0.0.1:9998")
        is_healthy = await client.check_health()
        assert is_healthy is False

    @pytest.mark.anyio
    @patch("backend.serving.ollama_client.httpx.AsyncClient.post")
    async def test_generate_success(self, mock_post: AsyncMock) -> None:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": {"content": "Sample model response from Ollama"}
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        client = OllamaClient(base_url="http://127.0.0.1:11434")
        result = await client.generate(prompt="Explain boiler efficiency")
        assert result == "Sample model response from Ollama"
