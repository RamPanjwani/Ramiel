"""Registry Loader for Ramiel Model Registry.

Phase 2: Model Registry & Router.
Parses and validates declarative model definitions from model_registry.yaml into
typed data structures without hardcoded model references.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field


class ModelEntry(BaseModel):
    """Specification of a single registered model."""

    id: str = Field(..., description="Unique identifier for the model")
    engine: Literal["vllm", "ollama"] = Field(..., description="Serving backend engine")
    path: str = Field(..., description="Local weights path or daemon model tag")
    task_tags: list[str] = Field(
        default_factory=list,
        description="Task categories this model handles (e.g. 'code', 'document', 'vision')",
    )
    min_vram_gb: int = Field(default=0, description="Minimum estimated VRAM in GB")
    fallback: str | None = Field(
        default=None, description="Optional fallback model ID if this model fails/OOMs"
    )


class ModelRegistry(BaseModel):
    """Container for all registered models."""

    models: list[ModelEntry] = Field(default_factory=list)


def load_registry(path: str | Path = "config/model_registry.yaml") -> list[ModelEntry]:
    """Load and validate the model registry YAML file.

    Args:
        path: Filesystem path to the model registry YAML configuration file.

    Returns:
        A list of validated ModelEntry instances.

    Raises:
        FileNotFoundError: If the registry file does not exist.
        ValueError: If model IDs are duplicated or fallback chains contain circular references.
    """
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(
            f"Model registry configuration not found: {config_path}"
        )

    with open(config_path, encoding="utf-8") as f:
        raw_data = yaml.safe_load(f)

    if not raw_data or "models" not in raw_data:
        return []

    registry = ModelRegistry(**raw_data)

    # Validate unique IDs
    seen_ids: set[str] = set()
    for model in registry.models:
        if model.id in seen_ids:
            raise ValueError(f"Duplicate model ID in registry: {model.id}")
        seen_ids.add(model.id)

    # Validate fallback existence
    for model in registry.models:
        if model.fallback and model.fallback not in seen_ids:
            raise ValueError(
                f"Model '{model.id}' references non-existent fallback '{model.fallback}'"
            )

    return registry.models
