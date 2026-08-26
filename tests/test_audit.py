"""Unit tests for audit logger and trace store (Phase 1)."""

from __future__ import annotations

import tempfile
from pathlib import Path

from backend.audit.logger import setup_logging
from backend.audit.trace_store import TraceStore


class TestAuditLogger:
    """Test structlog configuration."""

    def test_setup_logging_runs(self) -> None:
        log_file = Path(tempfile.mkdtemp()) / "test.log"
        setup_logging(log_level="DEBUG", log_file=str(log_file))
        assert log_file.parent.exists()


class TestTraceStore:
    """Test SQLite trace store persistence and queries."""

    def test_record_and_query(self) -> None:
        db_path = Path(tempfile.mkdtemp()) / "test_traces.db"
        store = TraceStore(db_path=db_path)

        event = {
            "task_id": "task-001",
            "session_id": "session-abc",
            "event_type": "chat_completion",
            "model_id": "reasoning-primary",
            "prompt": "Explain valve friction",
            "response": "Valve friction occurs due to...",
            "latency_ms": 124.5,
        }
        row_id = store.record(event)
        assert row_id > 0

        # Query by task ID
        traces = store.query("task-001")
        assert len(traces) == 1
        assert traces[0]["task_id"] == "task-001"
        assert traces[0]["prompt"] == "Explain valve friction"
        assert traces[0]["latency_ms"] == 124.5

    def test_query_session(self) -> None:
        db_path = Path(tempfile.mkdtemp()) / "test_traces.db"
        store = TraceStore(db_path=db_path)

        store.record({
            "task_id": "t1",
            "session_id": "s1",
            "event_type": "step",
            "prompt": "Step 1",
            "response": "Done",
        })
        store.record({
            "task_id": "t2",
            "session_id": "s1",
            "event_type": "step",
            "prompt": "Step 2",
            "response": "Done",
        })
        store.record({
            "task_id": "t3",
            "session_id": "s2",
            "event_type": "step",
            "prompt": "Other session",
            "response": "Done",
        })

        s1_traces = store.query_session("s1")
        assert len(s1_traces) == 2

        recent = store.get_recent(limit=10)
        assert len(recent) == 3
