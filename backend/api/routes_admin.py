"""Admin, audit, and monitoring endpoints.

Phase 2: Egress monitor status, trace store inspection, and model registry introspection.
"""

from __future__ import annotations

from fastapi import APIRouter, Query

from backend.audit.trace_store import TraceStore
from backend.router.model_router import ModelRouter
from backend.serving.ollama_client import OllamaClient
from backend.serving.vllm_client import VLLMClient

router = APIRouter(tags=["admin"])
_trace_store = TraceStore()
_model_router = ModelRouter()
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
        "models_registered": str(len(_model_router.models)),
        "phase": "2",
    }


@router.get("/models")
async def list_models() -> dict[str, object]:
    """List registered models and local serving status."""
    vllm_ok = await _vllm_client.check_health()
    ollama_ok = await _ollama_client.check_health()

    return {
        "models": [model.model_dump() for model in _model_router.models],
        "serving_engines": {
            "vllm": {"status": "online" if vllm_ok else "offline", "endpoint": _vllm_client.base_url},
            "ollama": {"status": "online" if ollama_ok else "offline", "endpoint": _ollama_client.base_url},
        },
        "phase": "2",
    }


@router.get("/route")
async def route_preview(prompt: str = Query(..., description="Prompt to classify and route")) -> dict[str, object]:
    """Simulate model routing for a given prompt."""
    task_tag = _model_router.classify_task(prompt)
    model_id = _model_router.route(task_tag)
    model_entry = _model_router.get_model(model_id)
    fallback_chain = _model_router.get_fallback_chain(model_id)

    return {
        "prompt": prompt,
        "task_tag": task_tag,
        "selected_model": model_id,
        "engine": model_entry.engine if model_entry else None,
        "fallback_chain": fallback_chain,
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
