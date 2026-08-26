"""Admin, audit, and monitoring endpoints.

Phase 1: Egress monitor status, trace store inspection, and serving health.
"""

from __future__ import annotations

from fastapi import APIRouter

from backend.audit.trace_store import TraceStore
from backend.serving.ollama_client import OllamaClient
from backend.serving.vllm_client import VLLMClient

router = APIRouter(tags=["admin"])
_trace_store = TraceStore()
_vllm_client = VLLMClient()
_ollama_client = OllamaClient()


@router.get("/health")
async def admin_health() -> dict[str, str]:
    """Detailed system health check."""
    vllm_ok = await _vllm_client.check_health()
    ollama_ok = await _ollama_client.check_health()

    return {
        "backend": "ok",
        "vllm_serving": "online" if vllm_ok else "offline",
        "ollama_serving": "online" if ollama_ok else "offline",
        "phase": "1",
    }


@router.get("/models")
async def list_models() -> dict[str, object]:
    """List serving status for local model backends."""
    vllm_ok = await _vllm_client.check_health()
    ollama_ok = await _ollama_client.check_health()

    return {
        "serving_engines": {
            "vllm": {"status": "online" if vllm_ok else "offline", "endpoint": _vllm_client.base_url},
            "ollama": {"status": "online" if ollama_ok else "offline", "endpoint": _ollama_client.base_url},
        },
        "phase": "1",
    }


@router.get("/egress")
async def egress_status() -> dict[str, object]:
    """Return current egress monitor status."""
    from backend.main import egress_monitor

    return {
        "running": egress_monitor.running,
        "total_checks": egress_monitor.total_checks,
        "violations": egress_monitor.violations,
        "status": "clean" if not egress_monitor.violations else "VIOLATION_DETECTED",
    }


@router.get("/traces")
async def list_traces(limit: int = 50) -> dict[str, object]:
    """Return recent execution traces from the SQLite audit store."""
    traces = _trace_store.get_recent(limit=limit)
    return {"count": len(traces), "traces": traces}
