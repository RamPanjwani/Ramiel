"""Admin, audit, and monitoring endpoints.

Phase 0: egress monitor status and model registry health stubs.
"""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["admin"])


@router.get("/health")
async def admin_health() -> dict[str, str]:
    """Detailed system health check."""
    return {
        "backend": "ok",
        "models_loaded": "0",
        "egress_violations": "0",
        "phase": "0",
    }


@router.get("/models")
async def list_models() -> dict[str, object]:
    """List registered models and their status.

    Phase 0 stub — returns empty roster.
    Phase 2+: will read model_registry.yaml and query serving health.
    """
    return {"models": [], "message": "Model registry not yet loaded (Phase 0)."}


@router.get("/egress")
async def egress_status() -> dict[str, object]:
    """Return current egress monitor status.

    Imported lazily to avoid circular dependency during Phase 0.
    """
    from backend.main import egress_monitor

    return {
        "running": egress_monitor.running,
        "total_checks": egress_monitor.total_checks,
        "violations": egress_monitor.violations,
        "status": "clean" if not egress_monitor.violations else "VIOLATION_DETECTED",
    }
