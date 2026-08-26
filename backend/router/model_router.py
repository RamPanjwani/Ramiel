"""Model Router for Ramiel.

Phase 2: Model Registry & Router.
Dispatches incoming sub-tasks to the best-fit local model based on task tags,
hardware availability, and declarative registry configurations. Handles fallback
chains when preferred models are unavailable or OOM.
"""

from __future__ import annotations

from typing import Any


class ModelRouter:
    """Routes agent tasks to appropriate local models using declarative registry rules."""

    def __init__(self, registry: list[dict[str, Any]] | None = None) -> None:
        self.registry = registry or []

    def route(self, task_tag: str) -> str:
        """Select the best-fit model ID matching the given task tag.

        Args:
            task_tag: The category tag for the task (e.g. 'code', 'document', 'vision', 'calc').

        Returns:
            The identifier of the selected model as configured in model_registry.yaml.

        Raises:
            NotImplementedError: Implementation pending Phase 2.
        """
        raise NotImplementedError("ModelRouter.route is not yet implemented.")

    def get_fallback(self, model_id: str) -> str | None:
        """Retrieve the configured fallback model ID if the primary model fails or OOMs.

        Args:
            model_id: The primary model identifier.

        Returns:
            The fallback model identifier, or None if no fallback is configured.

        Raises:
            NotImplementedError: Implementation pending Phase 2.
        """
        raise NotImplementedError("ModelRouter.get_fallback is not yet implemented.")
