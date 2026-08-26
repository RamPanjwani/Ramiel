"""Execution Trace Store for Ramiel.

Phase 1: Single Model & Basic Chat.
Persists and queries structured task lifecycle events, tool invocations, model calls,
and timestamps using a local SQLite database without external dependencies.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class TraceStore:
    """SQLite-backed storage and retrieval engine for execution traces and audit logs."""

    def __init__(self, db_path: str | Path = "logs/audit/traces.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Create a connection with row factory enabled."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Initialize the traces database schema if not present."""
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS traces (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT,
                    session_id TEXT,
                    event_type TEXT NOT NULL,
                    model_id TEXT,
                    prompt TEXT,
                    response TEXT,
                    metadata_json TEXT,
                    timestamp TEXT NOT NULL
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_traces_task_id ON traces (task_id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_traces_session_id ON traces (session_id)"
            )
            conn.commit()

    def record(self, event: dict[str, Any]) -> int:
        """Record an execution event or tool call trace into SQLite storage.

        Args:
            event: Event metadata containing task_id, session_id, event_type,
                model_id, prompt, response, timestamp, and arbitrary metadata.

        Returns:
            The inserted row ID.
        """
        task_id = event.get("task_id")
        session_id = event.get("session_id")
        event_type = event.get("event_type", "model_call")
        model_id = event.get("model_id")
        prompt = event.get("prompt")
        response = event.get("response")
        timestamp = event.get("timestamp") or datetime.now(timezone.utc).isoformat()

        # Extract extra metadata as JSON
        excluded_keys = {
            "task_id",
            "session_id",
            "event_type",
            "model_id",
            "prompt",
            "response",
            "timestamp",
        }
        metadata = {k: v for k, v in event.items() if k not in excluded_keys}
        metadata_json = json.dumps(metadata) if metadata else None

        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO traces (
                    task_id, session_id, event_type, model_id,
                    prompt, response, metadata_json, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    task_id,
                    session_id,
                    event_type,
                    model_id,
                    prompt,
                    response,
                    metadata_json,
                    timestamp,
                ),
            )
            conn.commit()
            return cursor.lastrowid or 0

    def query(self, task_id: str) -> list[dict[str, Any]]:
        """Query all recorded trace events associated with a specific task ID.

        Args:
            task_id: The unique task identifier to search for.

        Returns:
            A list of chronological trace event dictionaries for the task.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM traces WHERE task_id = ? ORDER BY id ASC",
                (task_id,),
            )
            rows = cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]

    def query_session(self, session_id: str) -> list[dict[str, Any]]:
        """Query all recorded trace events associated with a session ID."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM traces WHERE session_id = ? ORDER BY id ASC",
                (session_id,),
            )
            rows = cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]

    def get_recent(self, limit: int = 50) -> list[dict[str, Any]]:
        """Get recent trace records across all sessions/tasks."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM traces ORDER BY id DESC LIMIT ?",
                (limit,),
            )
            rows = cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]

    def _row_to_dict(self, row: sqlite3.Row) -> dict[str, Any]:
        """Convert a SQLite row to a dictionary, unpacking metadata_json."""
        d = dict(row)
        if d.get("metadata_json"):
            try:
                metadata = json.loads(d["metadata_json"])
                d.update(metadata)
            except json.JSONDecodeError:
                pass
        return d
