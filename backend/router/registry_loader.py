"""Registry Loader for Ramiel Model Registry.

Phase 2: Model Registry & Router.
Parses and validates declarative model definitions from model_registry.yaml.
"""

from __future__ import annotations

from typing import Any


def load_registry(path: str = "config/model_registry.yaml") -> list[dict[str, Any]]:
    """Load and validate the model registry YAML file.

    Args:
        path: Filesystem path to the model registry YAML configuration file.

    Returns:
        A list of parsed model specification dictionaries.

    Raises:
        NotImplementedError: Implementation pending Phase 2.
    """
    raise NotImplementedError("load_registry is not yet implemented.")
