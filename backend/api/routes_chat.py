"""Chat and prompt execution endpoints.

Phase 0: stub returning placeholder response.
Phase 1+: will connect to orchestrator for real model dispatch.
"""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    """Incoming chat prompt."""

    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    """Chat response envelope."""

    reply: str
    session_id: str
    model_used: str | None = None


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Process a chat prompt.

    Phase 0 stub — returns a fixed message.
    """
    return ChatResponse(
        reply=(
            "Ramiel is running (Phase 0 skeleton). Model serving not yet connected."
        ),
        session_id=request.session_id or "stub-session",
        model_used=None,
    )
