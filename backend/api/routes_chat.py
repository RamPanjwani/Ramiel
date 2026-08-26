"""Chat and prompt execution endpoints.

Phase 1: Single Model & Basic Chat.
Receives user prompts, queries local model serving (vLLM or Ollama),
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
from backend.serving.ollama_client import OllamaClient
from backend.serving.vllm_client import VLLMClient

logger = structlog.get_logger(__name__)
router = APIRouter(tags=["chat"])

# Singleton clients for local model serving & audit tracing
_trace_store = TraceStore()
_vllm_client = VLLMClient()
_ollama_client = OllamaClient()


class ChatRequest(BaseModel):
    """Incoming chat prompt."""

    message: str = Field(..., description="User prompt text")
    session_id: str | None = Field(default=None, description="Optional session tracking ID")
    model_id: str | None = Field(default=None, description="Requested model identifier")


class ChatResponse(BaseModel):
    """Chat response envelope."""

    reply: str
    session_id: str
    task_id: str
    model_used: str | None = None
    latency_ms: float | None = None


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Process a chat prompt through local model serving and record audit trace.

    Phase 1 implementation: Direct invocation to local vLLM/Ollama model with full trace logging.
    """
    session_id = request.session_id or f"session-{uuid.uuid4().hex[:8]}"
    task_id = f"task-{uuid.uuid4().hex[:8]}"
    start_time = time.perf_counter()

    logger.info(
        "chat.received",
        session_id=session_id,
        task_id=task_id,
        prompt_preview=request.message[:80],
    )

    model_used: str | None = None
    reply_text: str = ""

    # 1. Try local vLLM first
    if await _vllm_client.check_health():
        target_model = request.model_id or "reasoning-primary"
        try:
            reply_text = await _vllm_client.generate(
                prompt=request.message,
                model=target_model,
            )
            model_used = f"vllm:{target_model}"
        except (httpx.HTTPError, OSError, ConnectionError) as exc:
            logger.warning("chat.vllm_failed", error=str(exc))

    # 2. Try local Ollama if vLLM did not handle it
    if not reply_text and await _ollama_client.check_health():
        target_model = request.model_id or "llama3.2"
        try:
            reply_text = await _ollama_client.generate(
                prompt=request.message,
                model=target_model,
            )
            model_used = f"ollama:{target_model}"
        except (httpx.HTTPError, OSError, ConnectionError) as exc:
            logger.warning("chat.ollama_failed", error=str(exc))

    # 3. If no local serving backend is running, provide guidance
    if not reply_text:
        model_used = "system-offline-fallback"
        reply_text = (
            "Ramiel Workbench is operational in air-gap mode, but no local inference server "
            "(vLLM on port 8001 or Ollama on port 11434) responded.\n\n"
            "To serve models locally:\n"
            "  1. Run `./scripts/download_models.sh` (one-time setup)\n"
            "  2. Start local serving: `ollama serve` or `vllm serve /models/...`\n"
            "  3. Re-send your prompt."
        )

    latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

    # 4. Record structured audit trace to SQLite
    event_data: dict[str, Any] = {
        "task_id": task_id,
        "session_id": session_id,
        "event_type": "chat_completion",
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
        model_used=model_used,
        latency_ms=latency_ms,
    )

    return ChatResponse(
        reply=reply_text,
        session_id=session_id,
        task_id=task_id,
        model_used=model_used,
        latency_ms=latency_ms,
    )
