"""Tool Registry for Ramiel.

Phase 3: Tool Layer.
Maintains a registry of all available tools, their schemas, permission requirements,
and invocation interfaces for the agent orchestrator.
"""

from __future__ import annotations

import inspect
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from backend.tools.code_sandbox import CodeSandbox
from backend.tools.file_io import ScopedFileIO
from backend.tools.spreadsheet import SpreadsheetTool


@dataclass
class ToolDefinition:
    """Metadata and execution handler for a registered tool."""

    name: str
    description: str
    handler: Callable[..., Any]
    parameters: dict[str, Any] = field(default_factory=dict)


class ToolRegistry:
    """Central repository and discovery mechanism for agent tools."""

    def __init__(self, register_defaults: bool = True) -> None:
        self._tools: dict[str, ToolDefinition] = {}
        if register_defaults:
            self._register_default_tools()

    def _register_default_tools(self) -> None:
        """Register the built-in standalone tools."""
        file_io = ScopedFileIO()
        sandbox = CodeSandbox()
        spreadsheet = SpreadsheetTool()

        self.register(
            name="file_read",
            description="Read text content from a permitted file in data/ or demo_assets/.",
            handler=file_io.read,
            parameters={
                "path": {"type": "string", "description": "Relative file path"}
            },
        )
        self.register(
            name="file_write",
            description="Write text content to a permitted directory (data/uploads or logs/audit).",
            handler=file_io.write,
            parameters={
                "path": {"type": "string", "description": "Relative destination path"},
                "content": {"type": "string", "description": "Text content to write"},
            },
        )
        self.register(
            name="file_list",
            description="List directory contents inside permitted read roots.",
            handler=file_io.list_dir,
            parameters={"path": {"type": "string", "description": "Directory path"}},
        )
        self.register(
            name="code_exec",
            description="Execute Python or Bash code inside a network-isolated (--network none) sandbox.",
            handler=sandbox.execute,
            parameters={
                "code": {"type": "string", "description": "Code string to execute"},
                "language": {
                    "type": "string",
                    "enum": ["python", "bash"],
                    "default": "python",
                },
            },
        )
        self.register(
            name="spreadsheet_read",
            description="Read tabular data and sheet names from an Excel .xlsx spreadsheet.",
            handler=spreadsheet.read_excel,
            parameters={
                "path": {"type": "string", "description": "Path to .xlsx file"}
            },
        )
        self.register(
            name="spreadsheet_write",
            description="Write tabular data to an Excel .xlsx file.",
            handler=spreadsheet.write_excel,
            parameters={
                "path": {
                    "type": "string",
                    "description": "Destination .xlsx file path",
                },
                "data": {"type": "object", "description": "Columns dict or rows list"},
            },
        )
        self.register(
            name="spreadsheet_stats",
            description="Compute summary statistics (min, max, mean, count) for an Excel spreadsheet.",
            handler=spreadsheet.summary_stats,
            parameters={
                "path": {"type": "string", "description": "Path to .xlsx file"}
            },
        )

    def register(
        self,
        name: str,
        description: str,
        handler: Callable[..., Any],
        parameters: dict[str, Any] | None = None,
    ) -> None:
        """Register a new tool."""
        self._tools[name] = ToolDefinition(
            name=name,
            description=description,
            handler=handler,
            parameters=parameters or {},
        )

    def get_tool(self, name: str) -> ToolDefinition:
        """Retrieve a registered tool definition by name."""
        if name not in self._tools:
            raise KeyError(
                f"Tool '{name}' not found. Registered tools: {list(self._tools.keys())}"
            )
        return self._tools[name]

    def list_tools(self) -> list[str]:
        """List the identifiers of all registered tools."""
        return list(self._tools.keys())

    def get_schemas(self) -> list[dict[str, Any]]:
        """Return tool definitions formatted for LLM tool-calling schemas."""
        schemas: list[dict[str, Any]] = []
        for name, tool in self._tools.items():
            schemas.append(
                {
                    "name": name,
                    "description": tool.description,
                    "parameters": {
                        "type": "object",
                        "properties": tool.parameters,
                    },
                }
            )
        return schemas

    async def execute(self, name: str, **kwargs: Any) -> Any:
        """Execute a tool by name with arguments."""
        tool = self.get_tool(name)
        if inspect.iscoroutinefunction(tool.handler):
            return await tool.handler(**kwargs)
        return tool.handler(**kwargs)
