"""Integration tests for chat endpoint and admin routes (Phase 2)."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from backend.main import app


class TestChatEndpoint:
    """Test /api/chat auto-routing and trace recording."""

    @pytest.mark.anyio
    async def test_chat_offline_fallback(self) -> None:
        """When local model server is offline, endpoint returns guidance and records trace."""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            res = await ac.post(
                "/api/chat",
                json={"message": "Write a python script to parse logs", "session_id": "sess-test-1"},
            )
            assert res.status_code == 200
            data = res.json()
            assert "reply" in data
            assert data["session_id"] == "sess-test-1"
            assert data["task_tag"] == "code"
            assert data["model_used"] == "offline-routed:coder-primary"
            assert data["task_id"].startswith("task-")

    @pytest.mark.anyio
    @patch("backend.api.routes_chat._vllm_client.check_health", new_callable=AsyncMock)
    @patch("backend.api.routes_chat._vllm_client.generate", new_callable=AsyncMock)
    async def test_chat_auto_routing_code(
        self, mock_generate: AsyncMock, mock_health: AsyncMock
    ) -> None:
        """Coding prompts should auto-route to coder-primary."""
        mock_health.return_value = True
        mock_generate.return_value = "def parse_logs(): pass"

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            res = await ac.post(
                "/api/chat",
                json={"message": "Write a python function to compute factorial"},
            )
            assert res.status_code == 200
            data = res.json()
            assert data["task_tag"] == "code"
            assert data["model_used"] == "vllm:coder-primary"

    @pytest.mark.anyio
    @patch("backend.api.routes_chat._vllm_client.check_health", new_callable=AsyncMock)
    @patch("backend.api.routes_chat._vllm_client.generate", new_callable=AsyncMock)
    async def test_chat_auto_routing_document(
        self, mock_generate: AsyncMock, mock_health: AsyncMock
    ) -> None:
        """Document prompts should auto-route to reasoning-primary."""
        mock_health.return_value = True
        mock_generate.return_value = "Executive Summary: Inspection complete."

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            res = await ac.post(
                "/api/chat",
                json={"message": "Summarize the plant inspection report"},
            )
            assert res.status_code == 200
            data = res.json()
            assert data["task_tag"] == "document"
            assert data["model_used"] == "vllm:reasoning-primary"

    @pytest.mark.anyio
    async def test_admin_route_preview(self) -> None:
        """Admin route preview returns classification and target model."""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            res = await ac.get(
                "/api/admin/route",
                params={"prompt": "Write a python script"},
            )
            assert res.status_code == 200
            data = res.json()
            assert data["task_tag"] == "code"
            assert data["selected_model"] == "coder-primary"
            assert data["fallback_chain"] == ["coder-primary", "coder-fallback"]

    @pytest.mark.anyio
    async def test_admin_traces_endpoint(self) -> None:
        """Traces endpoint should return recorded chat events."""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            await ac.post(
                "/api/chat",
                json={"message": "Trace verification prompt"},
            )

            res = await ac.get("/api/admin/traces")
            assert res.status_code == 200
            data = res.json()
            assert data["count"] > 0
            assert len(data["traces"]) > 0

    @pytest.mark.anyio
    async def test_admin_health_endpoint(self) -> None:
        """Admin health endpoint reports phase 2 and serving status."""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            res = await ac.get("/api/admin/health")
            assert res.status_code == 200
            data = res.json()
            assert data["phase"] == "2"
            assert data["backend"] == "ok"
