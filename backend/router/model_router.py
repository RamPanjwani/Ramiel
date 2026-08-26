"""Model Router for Ramiel.

Phase 2: Model Registry & Router.
Dispatches incoming sub-tasks to the best-fit local model based on task tags,
hardware availability, and declarative registry configurations. Handles fallback
chains when preferred models are unavailable or OOM.
"""

from __future__ import annotations

import re
from pathlib import Path

import structlog
import yaml

from backend.router.registry_loader import ModelEntry, load_registry

logger = structlog.get_logger(__name__)

# Keywords for rule-based task classification
_CODE_KEYWORDS = re.compile(
    r"\b(def|class|function|import|python|script|code|bug|refactor|compile|syntax|git|bash|sql|docker|regex|api|async|unittest|pytest)\b",
    re.IGNORECASE,
)
_VISION_KEYWORDS = re.compile(
    r"\b(drawing|p&id|pnid|diagram|schematic|scan|image|photo|ocr|blueprint|flowsheet|instrumentation)\b",
    re.IGNORECASE,
)
_CALC_KEYWORDS = re.compile(
    r"\b(calculate|calculation|formula|friction|reynolds|head loss|pump|efficiency|thermodynamic|pressure drop|mass balance|integral|derivative)\b",
    re.IGNORECASE,
)
_DOCUMENT_KEYWORDS = re.compile(
    r"\b(summarize|summary|approval note|draft|report|memo|sop|manual|procedure|policy|brief|minutes|board deck)\b",
    re.IGNORECASE,
)


class ModelRouter:
    """Routes agent tasks to appropriate local models using declarative registry rules."""

    def __init__(
        self,
        registry: list[ModelEntry] | None = None,
        registry_path: str | Path = "config/model_registry.yaml",
    ) -> None:
        if registry is not None:
            self.models = registry
        else:
            try:
                self.models = load_registry(registry_path)
            except (FileNotFoundError, ValueError, yaml.YAMLError, OSError) as exc:
                logger.warning("model_router.registry_load_failed", error=str(exc))
                self.models = []

        self._model_by_id: dict[str, ModelEntry] = {m.id: m for m in self.models}

    def classify_task(self, prompt: str) -> str:
        """Classify a prompt into a task category tag.

        Returns one of: 'code', 'vision', 'calc', 'document', 'general_qa'.
        """
        if _CODE_KEYWORDS.search(prompt):
            return "code"
        if _VISION_KEYWORDS.search(prompt):
            return "vision"
        if _CALC_KEYWORDS.search(prompt):
            return "calc"
        if _DOCUMENT_KEYWORDS.search(prompt):
            return "document"
        return "general_qa"

    def route(self, task_tag: str) -> str:
        """Select the best-fit model ID matching the given task tag.

        Args:
            task_tag: The category tag for the task ('code', 'document', 'vision', 'calc', etc.).

        Returns:
            The identifier of the selected model as configured in model_registry.yaml.

        Raises:
            ValueError: If no model in the registry matches the tag or default.
        """
        # 1. Match exact task tag
        for model in self.models:
            if task_tag in model.task_tags:
                return model.id

        # 2. Fallback to general_qa / document reasoning model
        for model in self.models:
            if "general_qa" in model.task_tags or "document" in model.task_tags:
                return model.id

        # 3. Ultimate fallback: first available model
        if self.models:
            return self.models[0].id

        raise ValueError(f"No models available in registry to handle task tag: '{task_tag}'")

    def route_model(self, task_tag: str) -> ModelEntry:
        """Return the complete ModelEntry matching the task tag."""
        model_id = self.route(task_tag)
        return self._model_by_id[model_id]

    def get_model(self, model_id: str) -> ModelEntry | None:
        """Retrieve a ModelEntry by ID."""
        return self._model_by_id.get(model_id)

    def get_fallback(self, model_id: str) -> str | None:
        """Retrieve the configured fallback model ID if the primary model fails or OOMs.

        Args:
            model_id: The primary model identifier.

        Returns:
            The fallback model identifier, or None if no fallback is configured.
        """
        model = self._model_by_id.get(model_id)
        if model and model.fallback:
            return model.fallback
        return None

    def get_fallback_chain(self, model_id: str) -> list[str]:
        """Return the full chain of fallback model IDs starting from model_id."""
        chain: list[str] = [model_id]
        current_id: str | None = model_id
        visited: set[str] = {model_id}

        while current_id:
            fallback = self.get_fallback(current_id)
            if fallback and fallback not in visited:
                chain.append(fallback)
                visited.add(fallback)
                current_id = fallback
            else:
                break
        return chain
