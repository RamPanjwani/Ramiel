"""Ramiel — Sovereign On-Premise Agentic AI Workbench.

FastAPI application entrypoint.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes_admin import router as admin_router
from backend.api.routes_chat import router as chat_router
from backend.api.routes_upload import router as upload_router
from backend.security.egress_monitor import EgressMonitor

logger = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Singleton egress monitor — started on app boot, queryable via admin routes.
# ---------------------------------------------------------------------------
egress_monitor = EgressMonitor()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Startup / shutdown lifecycle."""
    logger.info("ramiel.startup", phase="0-skeleton")
    egress_monitor.start()
    yield
    egress_monitor.stop()
    logger.info("ramiel.shutdown")


app = FastAPI(
    title="Ramiel — Sovereign AI Workbench",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — localhost only, never expose to external networks.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount route groups.
app.include_router(chat_router, prefix="/api")
app.include_router(upload_router, prefix="/api")
app.include_router(admin_router, prefix="/api/admin")


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Liveness probe — confirms the API is running."""
    return {"status": "ok", "service": "ramiel-backend", "phase": "0"}
