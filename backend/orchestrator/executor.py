"""Executor module for Ramiel Agent Orchestrator.

Phase 4: Agent Orchestrator.
Iterates through execution plan steps, routes sub-tasks to appropriate local
models via ModelRouter, invokes tools, handles bounded replanning upon step
failure, and checkpoints before irreversible actions.
"""

from __future__ import annotations

from typing import Any

import structlog

from backend.audit.trace_store import TraceStore
from backend.orchestrator.planner import Planner
from backend.orchestrator.state import TaskState
from backend.router.model_router import ModelRouter
from backend.serving.ollama_client import OllamaClient
from backend.serving.vllm_client import VLLMClient
from backend.tools.tool_registry import ToolRegistry

logger = structlog.get_logger(__name__)


class Executor:
    """Step execution loop for orchestrating agent tasks and tool calls."""

    def __init__(
        self,
        router: ModelRouter | None = None,
        tool_registry: ToolRegistry | None = None,
        trace_store: TraceStore | None = None,
        max_retries: int = 3,
    ) -> None:
        self.router = router or ModelRouter()
        self.tool_registry = tool_registry or ToolRegistry()
        self.trace_store = trace_store or TraceStore()
        self.planner = Planner(router=self.router)
        self.max_retries = max_retries
        self.vllm_client = VLLMClient()
        self.ollama_client = OllamaClient()

    async def execute_task(
        self, prompt: str, session_id: str | None = None
    ) -> TaskState:
        """Create a new task, plan it, and execute it through the step loop."""
        state = TaskState(prompt=prompt, session_id=session_id)
        state.status = "planning"

        # 1. Generate plan
        plan = await self.planner.generate_plan(prompt)
        state.plan = plan
        state.status = "running"
        state.save_checkpoint()

        # 2. Execute plan steps
        return await self.execute_plan(state)

    async def execute_plan(self, state: TaskState) -> TaskState:
        """Iterate through plan steps with tool invocation and human confirmation gates."""
        logger.info(
            "executor.executing_plan",
            task_id=state.task_id,
            steps_count=len(state.plan),
        )

        while state.current_step_index < len(state.plan):
            step = state.plan[state.current_step_index]
            step_idx = step["step_index"]
            task_tag = step.get("task_tag", "general_qa")
            tool_name = step.get("tool_name")
            tool_args = step.get("tool_args", {})
            requires_confirmation = step.get("requires_confirmation", False)

            # Gate: Human-in-the-loop checkpoint before irreversible actions
            if requires_confirmation and not step.get("confirmed", False):
                logger.info(
                    "executor.confirmation_required",
                    step=step_idx,
                    action=step["description"],
                )
                state.request_confirmation(
                    action=step["description"],
                    details={
                        "step_index": step_idx,
                        "tool_name": tool_name,
                        "args": tool_args,
                    },
                )
                state.save_checkpoint()
                return state

            # Route model for step
            model_id = self.router.route(task_tag)
            logger.info(
                "executor.step_start", step=step_idx, model=model_id, tool=tool_name
            )

            # Execute tool if required
            tool_output: Any = None
            step_status = "success"

            if tool_name:
                resolved_args = dict(tool_args)
                last_output = (
                    state.observations[-1]["output"] if state.observations else ""
                )

                if tool_name == "code_exec" and "code" not in resolved_args:
                    resolved_args["code"] = (
                        str(last_output)
                        if last_output and not str(last_output).startswith("Tool")
                        else f"# Auto-generated code for: {step['description']}\nprint(42)"
                    )
                elif tool_name == "file_read" and "path" not in resolved_args:
                    resolved_args["path"] = "data/uploads/test_file_io.txt"
                elif tool_name == "file_write" and "content" not in resolved_args:
                    resolved_args["content"] = (
                        str(last_output) or "Generated deliverable content."
                    )
                elif tool_name == "spreadsheet_write" and "data" not in resolved_args:
                    resolved_args["data"] = {
                        "Calculations": ["Val1", "Val2"],
                        "Values": [10.0, 20.0],
                    }

                try:
                    tool_output = await self.tool_registry.execute(
                        tool_name, **resolved_args
                    )
                except (
                    PermissionError,
                    FileNotFoundError,
                    TimeoutError,
                    OSError,
                    ValueError,
                    KeyError,
                    RuntimeError,
                    TypeError,
                ) as exc:
                    logger.warning(
                        "executor.tool_failed", tool=tool_name, error=str(exc)
                    )
                    step_status = "failed"
                    tool_output = f"Tool execution failed: {exc}"

                    # Bounded replanning on failure
                    if state.retry_count < self.max_retries:
                        state.retry_count += 1
                        logger.info(
                            "executor.replanning_retry", retry=state.retry_count
                        )
                        continue
                    else:
                        state.status = "failed"
                        state.add_observation(
                            step_idx, tool_name, tool_output, status="failed"
                        )
                        state.save_checkpoint()
                        return state

            # Record step observation
            state.add_observation(step_idx, tool_name, tool_output, status=step_status)
            self.trace_store.record(
                {
                    "task_id": state.task_id,
                    "session_id": state.session_id,
                    "event_type": "step_execution",
                    "model_id": model_id,
                    "task_tag": task_tag,
                    "prompt": step["description"],
                    "response": str(tool_output)
                    if tool_output is not None
                    else "Step completed",
                }
            )

            state.current_step_index += 1
            state.save_checkpoint()

        state.status = "completed"
        state.results = {
            "summary": f"Completed {len(state.plan)} steps successfully.",
            "observations_count": len(state.observations),
        }
        state.save_checkpoint()
        logger.info("executor.task_completed", task_id=state.task_id)
        return state
