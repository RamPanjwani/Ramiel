"""Tool Registry for Ramiel.

Phase 3: Tool Layer.
Maintains a registry of all available tools, their permission requirements,
and invocation interfaces for the agent orchestrator.
"""

from __future__ import annotations

from typing import Any


class ToolRegistry:
    """Central repository and discovery mechanism for agent tools."""

    def __init__(self) -> None:
        self._tools: dict[str, Any] = {}

    def get_tool(self, name: str) -> Any:
        """Retrieve a registered tool instance by name.

        Args:
            name: Identifier of the tool (e.g. 'file_io', 'code_sandbox', 'spreadsheet').

        Returns:
            The instantiated tool handler.

        Raises:
            KeyError: If the requested tool is not found.
            NotImplementedError: Implementation pending Phase 3.
        """
        raise NotImplementedError("ToolRegistry.get_tool is not yet implemented.")

    def list_tools(self) -> list[str]:
        """List the identifiers of all registered tools.

        Returns:
            A list of tool names available in the registry.

        Raises:
            NotImplementedError: Implementation pending Phase 3.
        """
        raise NotImplementedError("ToolRegistry.list_tools is not yet implemented.")
