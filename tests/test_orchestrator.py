"""Orchestrator Tests — Phase 4.

Validates:
1. Planner structured step-plan generation across task tags.
2. TaskState SQLite checkpoint persistence, restoration, and confirmation gating.
3. Executor ReAct execution loop, tool invocation, and bounded replanning.
4. OrchestrationGraph end-to-end workflow execution and resumption.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from backend.audit.trace_store import TraceStore
from backend.orchestrator.executor import Executor
from backend.orchestrator.graph import OrchestrationGraph
from backend.orchestrator.planner import Planner
from backend.orchestrator.state import TaskState
from backend.router.model_router import ModelRouter
from backend.tools.tool_registry import ToolRegistry


class TestPlanner:
    """Test Planner multi-step plan generation."""

    @pytest.fixture
    def planner(self) -> Planner:
        return Planner()

    @pytest.mark.anyio
    async def test_generates_structured_plan_code(self, planner: Planner) -> None:
        """Planner generates code-specific multi-step plan."""
        plan = await planner.generate_plan("Write a python script to validate checksums")
        assert len(plan) >= 3
        assert plan[0]["task_tag"] == "code"
        assert any(step.get("tool_name") == "code_exec" for step in plan)

    @pytest.mark.anyio
    async def test_generates_structured_plan_document(self, planner: Planner) -> None:
        """Document plan includes human confirmation gate before final write."""
        plan = await planner.generate_plan("Summarize inspection report into an approval note")
        assert len(plan) >= 3
        assert plan[0]["task_tag"] == "document"
        assert any(step.get("requires_confirmation") is True for step in plan)


class TestTaskState:
    """Test TaskState checkpoint persistence and confirmation gating."""

    def test_checkpoint_save_and_load(self) -> None:
        """State can be saved to SQLite and restored accurately."""
        db_path = Path(tempfile.mkdtemp()) / "test_checkpoints.db"
        state = TaskState(prompt="Test prompt", session_id="sess-123")
        state.status = "running"
        state.add_observation(1, "file_read", "file content read")
        task_id = state.save_checkpoint(db_path=db_path)

        # Restore from checkpoint
        restored = TaskState.load_checkpoint(task_id, db_path=db_path)
        assert restored.task_id == task_id
        assert restored.session_id == "sess-123"
        assert restored.status == "running"
        assert len(restored.observations) == 1
        assert restored.observations[0]["tool_name"] == "file_read"

    def test_confirmation_lifecycle(self) -> None:
        """State handles request_confirmation and confirm transitions."""
        state = TaskState(prompt="Delete file")
        state.request_confirmation("file_delete", {"path": "data/uploads/old.txt"})
        assert state.status == "waiting_confirmation"
        assert state.pending_confirmation is not None
        assert state.pending_confirmation["action"] == "file_delete"

        state.confirm()
        assert state.status == "running"
        assert state.pending_confirmation is None


class TestExecutor:
    """Test Executor step execution loop and tool coordination."""

    @pytest.fixture
    def executor(self) -> Executor:
        trace_db = Path(tempfile.mkdtemp()) / "test_traces.db"
        return Executor(
            router=ModelRouter(),
            tool_registry=ToolRegistry(),
            trace_store=TraceStore(db_path=trace_db),
        )

    @pytest.mark.anyio
    async def test_executes_plan_steps(self, executor: Executor) -> None:
        """Executor executes multi-step task and records observations."""
        state = await executor.execute_task("Write a python script to calculate 10 + 20")
        assert state.status == "completed"
        assert len(state.observations) >= 2
        assert state.results.get("summary") is not None

    @pytest.mark.anyio
    async def test_human_checkpoint_gate(self, executor: Executor) -> None:
        """Executor pauses at steps requiring human confirmation."""
        sample_path = Path("data/uploads/test_file_io.txt")
        sample_path.parent.mkdir(parents=True, exist_ok=True)
        sample_path.write_text("Sample Inspection Report Content", encoding="utf-8")

        prompt = "Summarize the plant report and publish approval note"
        state = await executor.execute_task(prompt)

        # Should halt at confirmation step
        assert state.status == "waiting_confirmation"
        assert state.pending_confirmation is not None

        # Operator confirms
        state.confirm()
        resumed_state = await executor.execute_plan(state)
        assert resumed_state.status == "completed"


class TestOrchestrationGraph:
    """Test OrchestrationGraph end-to-end workflow execution."""

    @pytest.fixture
    def graph(self) -> OrchestrationGraph:
        return OrchestrationGraph()

    @pytest.mark.anyio
    async def test_graph_run(self, graph: OrchestrationGraph) -> None:
        """Graph executes workflow and returns final state dict."""
        result = await graph.run("Write a python function to check prime numbers")
        assert result["status"] == "completed"
        assert result["task_id"].startswith("task-")
        assert len(result["observations"]) >= 2
