"""Task State and Checkpointing for Ramiel Agent Orchestrator.

Phase 4: Agent Orchestrator.
Manages persistent state snapshots, human-in-the-loop checkpoint gates,
and task resumption across agent steps using local SQLite storage.
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

TaskStatus = Literal["pending", "planning", "running", "waiting_confirmation", "completed", "failed"]


class TaskState:
    """Manages task lifecycle state and persistent checkpoints."""

    def __init__(
        self,
        task_id: str | None = None,
        session_id: str | None = None,
        prompt: str = "",
        state_data: dict[str, Any] | None = None,
    ) -> None:
        self.task_id = task_id or f"task-{uuid.uuid4().hex[:8]}"
        self.session_id = session_id or f"session-{uuid.uuid4().hex[:8]}"
        self.prompt = prompt
        self.status: TaskStatus = "pending"
        self.plan: list[dict[str, Any]] = []
        self.current_step_index: int = 0
        self.observations: list[dict[str, Any]] = []
        self.results: dict[str, Any] = {}
        self.pending_confirmation: dict[str, Any] | None = None
        self.retry_count: int = 0
        self.created_at: str = datetime.now(timezone.utc).isoformat()
        self.updated_at: str = self.created_at

        if state_data:
            self._hydrate(state_data)

    def _hydrate(self, data: dict[str, Any]) -> None:
        """Hydrate instance fields from a state dictionary."""
        self.task_id = data.get("task_id", self.task_id)
        self.session_id = data.get("session_id", self.session_id)
        self.prompt = data.get("prompt", self.prompt)
        self.status = data.get("status", self.status)
        self.plan = data.get("plan", [])
        self.current_step_index = data.get("current_step_index", 0)
        self.observations = data.get("observations", [])
        self.results = data.get("results", {})
        self.pending_confirmation = data.get("pending_confirmation")
        self.retry_count = data.get("retry_count", 0)
        self.created_at = data.get("created_at", self.created_at)
        self.updated_at = data.get("updated_at", self.updated_at)

    def to_dict(self) -> dict[str, Any]:
        """Convert state to a JSON-serializable dictionary."""
        return {
            "task_id": self.task_id,
            "session_id": self.session_id,
            "prompt": self.prompt,
            "status": self.status,
            "plan": self.plan,
            "current_step_index": self.current_step_index,
            "observations": self.observations,
            "results": self.results,
            "pending_confirmation": self.pending_confirmation,
            "retry_count": self.retry_count,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def add_observation(self, step_index: int, tool_name: str | None, output: Any, status: str = "success") -> None:
        """Record an observation for a completed step."""
        self.observations.append({
            "step_index": step_index,
            "tool_name": tool_name,
            "output": output,
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def request_confirmation(self, action: str, details: dict[str, Any]) -> None:
        """Halt execution for human-in-the-loop approval before irreversible actions."""
        self.status = "waiting_confirmation"
        self.pending_confirmation = {
            "action": action,
            "details": details,
            "requested_at": datetime.now(timezone.utc).isoformat(),
        }
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def confirm(self) -> None:
        """Approve pending confirmation and resume execution."""
        self.status = "running"
        if 0 <= self.current_step_index < len(self.plan):
            self.plan[self.current_step_index]["confirmed"] = True
        self.pending_confirmation = None
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def save_checkpoint(self, db_path: str | Path = "logs/audit/checkpoints.db") -> str:
        """Persist current task state snapshot to SQLite storage."""
        path = Path(db_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.updated_at = datetime.now(timezone.utc).isoformat()

        with sqlite3.connect(str(path)) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS checkpoints (
                    task_id TEXT PRIMARY KEY,
                    session_id TEXT,
                    status TEXT,
                    state_json TEXT,
                    updated_at TEXT
                )
                """
            )
            conn.execute(
                """
                INSERT OR REPLACE INTO checkpoints (task_id, session_id, status, state_json, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    self.task_id,
                    self.session_id,
                    self.status,
                    json.dumps(self.to_dict()),
                    self.updated_at,
                ),
            )
            conn.commit()
        return self.task_id

    @classmethod
    def load_checkpoint(cls, task_id: str, db_path: str | Path = "logs/audit/checkpoints.db") -> TaskState:
        """Load a previously saved task checkpoint by task ID."""
        path = Path(db_path)
        if not path.exists():
            raise FileNotFoundError(f"Checkpoint database not found: {path}")

        with sqlite3.connect(str(path)) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT state_json FROM checkpoints WHERE task_id = ?",
                (task_id,),
            )
            row = cursor.fetchone()
            if not row:
                raise KeyError(f"No checkpoint found for task ID: {task_id}")

            data = json.loads(row["state_json"])
            return cls(state_data=data)
