"""State Graph Orchestration for Ramiel Agent.

Phase 4: Agent Orchestrator.
Defines the state graph coordinating planning, routing, tool invocation,
human confirmation checkpoints, and deliverable generation.
"""

from __future__ import annotations

from typing import Any

import structlog

from backend.orchestrator.executor import Executor
from backend.orchestrator.planner import Planner
from backend.orchestrator.state import TaskState
from backend.router.model_router import ModelRouter
from backend.tools.tool_registry import ToolRegistry

logger = structlog.get_logger(__name__)


class OrchestrationGraph:
    """State graph coordinator for Ramiel multi-step agent workflows."""

    def __init__(
        self,
        router: ModelRouter | None = None,
        tool_registry: ToolRegistry | None = None,
    ) -> None:
        self.router = router or ModelRouter()
        self.tool_registry = tool_registry or ToolRegistry()
        self.planner = Planner(router=self.router)
        self.executor = Executor(router=self.router, tool_registry=self.tool_registry)

    async def run(self, prompt: str, session_id: str | None = None) -> dict[str, Any]:
        """Execute the complete agent workflow graph from prompt to delivery.

        Flow:
            [Prompt] -> (Planning Node) -> (Route Node) -> (Step Exec Loop)
                     -> [Optional Checkpoint Gate] -> (Completion Node)
        """
        logger.info("orchestration_graph.start", prompt_preview=prompt[:60])
        state = await self.executor.execute_task(prompt, session_id=session_id)
        return state.to_dict()

    async def resume(self, task_id: str, confirmation_approved: bool = True) -> dict[str, Any]:
        """Resume a task halted at a human-in-the-loop checkpoint gate."""
        state = TaskState.load_checkpoint(task_id)
        if state.status == "waiting_confirmation":
            if confirmation_approved:
                state.confirm()
                state = await self.executor.execute_plan(state)
            else:
                state.status = "failed"
                state.results["rejection"] = "Operator declined action."
                state.save_checkpoint()

        return state.to_dict()
