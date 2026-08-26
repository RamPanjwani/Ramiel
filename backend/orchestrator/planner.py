"""Planner module for Ramiel Agent Orchestrator.

Phase 4: Agent Orchestrator.
Parses user intent and generates a structured step-by-step execution plan using
the reasoning model resolved from the model registry.
"""

from __future__ import annotations

from typing import Any

import structlog

from backend.router.model_router import ModelRouter

logger = structlog.get_logger(__name__)


class Planner:
    """Step-plan generator for agent orchestration."""

    def __init__(self, router: ModelRouter | None = None) -> None:
        self.router = router or ModelRouter()

    async def generate_plan(
        self, prompt: str, context: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Generate a structured step-by-step execution plan from a prompt and context.

        Args:
            prompt: The user request or instruction.
            context: Optional execution context containing session metadata, available tools, etc.

        Returns:
            A list of step definitions, each containing:
                - step_index: 1-indexed step sequence number.
                - description: Human-readable action description.
                - task_tag: Tag for model routing (e.g. 'code', 'document', 'calc', 'vision').
                - tool_name: Optional tool to invoke (e.g. 'code_exec', 'file_read', 'spreadsheet_read').
                - tool_args: Arguments for the tool invocation.
                - requires_confirmation: True if irreversible/destructive action requiring human approval.
        """
        task_tag = self.router.classify_task(prompt)
        logger.info("planner.generating", prompt_preview=prompt[:60], task_tag=task_tag)

        # Generate structured plan according to task category
        if task_tag == "code":
            return [
                {
                    "step_index": 1,
                    "description": "Analyze technical requirements and generate verified Python code",
                    "task_tag": "code",
                    "tool_name": None,
                    "tool_args": {},
                    "requires_confirmation": False,
                },
                {
                    "step_index": 2,
                    "description": "Execute generated code in network-isolated Docker sandbox (--network none)",
                    "task_tag": "code",
                    "tool_name": "code_exec",
                    "tool_args": {"language": "python"},
                    "requires_confirmation": False,
                },
                {
                    "step_index": 3,
                    "description": "Save verified executable and execution log to data/uploads",
                    "task_tag": "code",
                    "tool_name": "file_write",
                    "tool_args": {"path": "data/uploads/solution.py"},
                    "requires_confirmation": False,
                },
            ]

        if task_tag == "calc":
            return [
                {
                    "step_index": 1,
                    "description": "Parse engineering parameters, equations, and physical boundary values",
                    "task_tag": "calc",
                    "tool_name": None,
                    "tool_args": {},
                    "requires_confirmation": False,
                },
                {
                    "step_index": 2,
                    "description": "Perform step-by-step mathematical calculations in sandbox runtime",
                    "task_tag": "calc",
                    "tool_name": "code_exec",
                    "tool_args": {"language": "python"},
                    "requires_confirmation": False,
                },
                {
                    "step_index": 3,
                    "description": "Format calculation steps into structured spreadsheet audit workbook",
                    "task_tag": "calc",
                    "tool_name": "spreadsheet_write",
                    "tool_args": {"path": "data/uploads/calculation_audit.xlsx"},
                    "requires_confirmation": False,
                },
            ]

        if task_tag == "document":
            return [
                {
                    "step_index": 1,
                    "description": "Read and extract findings from target document or internal SOP",
                    "task_tag": "document",
                    "tool_name": "file_read",
                    "tool_args": {},
                    "requires_confirmation": False,
                },
                {
                    "step_index": 2,
                    "description": "Synthesize findings and draft formal executive approval note",
                    "task_tag": "document",
                    "tool_name": None,
                    "tool_args": {},
                    "requires_confirmation": False,
                },
                {
                    "step_index": 3,
                    "description": "Require human confirmation before publishing final approval note deliverable",
                    "task_tag": "document",
                    "tool_name": "file_write",
                    "tool_args": {"path": "data/uploads/approval_note.docx"},
                    "requires_confirmation": True,
                },
            ]

        if task_tag == "vision":
            return [
                {
                    "step_index": 1,
                    "description": "Ingest P&ID drawing / scan and extract component tags and connectivity",
                    "task_tag": "vision",
                    "tool_name": None,
                    "tool_args": {},
                    "requires_confirmation": False,
                },
                {
                    "step_index": 2,
                    "description": "Cross-reference extracted tags against local engineering specifications",
                    "task_tag": "document",
                    "tool_name": None,
                    "tool_args": {},
                    "requires_confirmation": False,
                },
                {
                    "step_index": 3,
                    "description": "Compile structured drawing readout report",
                    "task_tag": "document",
                    "tool_name": "file_write",
                    "tool_args": {"path": "data/uploads/drawing_analysis.txt"},
                    "requires_confirmation": False,
                },
            ]

        # Default general Q&A multi-step plan
        return [
            {
                "step_index": 1,
                "description": "Analyze inquiry and construct reasoned response using local knowledge base",
                "task_tag": "general_qa",
                "tool_name": None,
                "tool_args": {},
                "requires_confirmation": False,
            },
            {
                "step_index": 2,
                "description": "Finalize and verify answer grounding",
                "task_tag": "general_qa",
                "tool_name": None,
                "tool_args": {},
                "requires_confirmation": False,
            },
        ]
