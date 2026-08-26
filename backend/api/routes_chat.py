"""Chat and prompt execution endpoints.

Phase 2: Model Registry & Router.
Receives user prompts, auto-classifies task type (code, doc, vision, calc, general_qa),
routes to the optimal local model via ModelRouter with fallback support,
records execution traces to SQLite audit store, and returns structured responses.
"""

from __future__ import annotations

import time
import uuid
from typing import Any

import httpx
import structlog
from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.audit.trace_store import TraceStore
from backend.router.model_router import ModelRouter
from backend.serving.ollama_client import OllamaClient
from backend.serving.vllm_client import VLLMClient

logger = structlog.get_logger(__name__)
router = APIRouter(tags=["chat"])

# Singleton clients for local model serving, routing & audit tracing
_trace_store = TraceStore()
_model_router = ModelRouter()
_vllm_client = VLLMClient()
_ollama_client = OllamaClient()


class ChatRequest(BaseModel):
    """Incoming chat prompt."""

    message: str = Field(..., description="User prompt text")
    session_id: str | None = Field(
        default=None, description="Optional session tracking ID"
    )
    model_id: str | None = Field(
        default=None,
        description="Optional explicit model override (bypasses auto-routing)",
    )


class ChatResponse(BaseModel):
    """Chat response envelope."""

    reply: str
    session_id: str
    task_id: str
    task_tag: str
    model_used: str | None = None
    latency_ms: float | None = None


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Process a chat prompt with automatic model routing and audit trace logging.

    Phase 2 implementation:
    1. Classify prompt task tag (code, document, vision, calc, general_qa).
    2. Route to target model from model_registry.yaml.
    3. Attempt generation on primary engine (vLLM/Ollama), cascading down fallback chain on error.
    4. Record trace to SQLite store.
    """
    session_id = request.session_id or f"session-{uuid.uuid4().hex[:8]}"
    task_id = f"task-{uuid.uuid4().hex[:8]}"
    start_time = time.perf_counter()

    # Classify task tag
    task_tag = _model_router.classify_task(request.message)

    # Determine target model ID
    if request.model_id:
        target_model_id = request.model_id
    else:
        try:
            target_model_id = _model_router.route(task_tag)
        except ValueError:
            target_model_id = "reasoning-primary"

    logger.info(
        "chat.received",
        session_id=session_id,
        task_id=task_id,
        task_tag=task_tag,
        target_model=target_model_id,
        prompt_preview=request.message[:80],
    )

    model_used: str | None = None
    reply_text: str = ""

    # Get model candidate chain (primary + fallbacks)
    model_chain = _model_router.get_fallback_chain(target_model_id)

    for candidate_id in model_chain:
        candidate_entry = _model_router.get_model(candidate_id)
        engine = candidate_entry.engine if candidate_entry else "vllm"
        model_path = candidate_entry.path if candidate_entry else candidate_id

        if engine == "vllm" and await _vllm_client.check_health():
            try:
                reply_text = await _vllm_client.generate(
                    prompt=request.message,
                    model=model_path,
                )
                model_used = f"vllm:{candidate_id}"
                break
            except (httpx.HTTPError, OSError, ConnectionError) as exc:
                logger.warning("chat.vllm_failed", model=candidate_id, error=str(exc))

        elif engine == "ollama" and await _ollama_client.check_health():
            try:
                reply_text = await _ollama_client.generate(
                    prompt=request.message,
                    model=model_path,
                )
                model_used = f"ollama:{candidate_id}"
                break
            except (httpx.HTTPError, OSError, ConnectionError) as exc:
                logger.warning("chat.ollama_failed", model=candidate_id, error=str(exc))

    # If no model in fallback chain responded, provide offline guidance
    if not reply_text:
        model_used = f"offline-routed:{target_model_id}"
        reply_text = (
            f"Task routed to **{target_model_id}** (task tag: `{task_tag}`), "
            "but local model serving is currently offline.\n\n"
            "To serve models locally:\n"
            "  1. Run `./scripts/download_models.sh` (one-time network setup)\n"
            f"  2. Launch local daemon for engine: `{target_model_id}`\n"
            "  3. Re-send prompt to execute on-premise."
        )

    latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

    # Record structured audit trace to SQLite
    event_data: dict[str, Any] = {
        "task_id": task_id,
        "session_id": session_id,
        "event_type": "chat_completion",
        "task_tag": task_tag,
        "model_id": model_used,
        "prompt": request.message,
        "response": reply_text,
        "latency_ms": latency_ms,
    }
    _trace_store.record(event_data)

    logger.info(
        "chat.completed",
        session_id=session_id,
        task_id=task_id,
        task_tag=task_tag,
        model_used=model_used,
        latency_ms=latency_ms,
    )

    return ChatResponse(
        reply=reply_text,
        session_id=session_id,
        task_id=task_id,
        task_tag=task_tag,
        model_used=model_used,
        latency_ms=latency_ms,
    )
