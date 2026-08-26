"""Model Router Tests — Phase 2.

Validates:
1. Model registry YAML loading & validation.
2. Task classification for code, vision, calc, document, and general QA prompts.
3. Tag-based model dispatch (PRD §6.1 acceptance criterion).
4. Fallback chain retrieval on model failure or OOM.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from backend.router.model_router import ModelRouter
from backend.router.registry_loader import load_registry


class TestRegistryLoader:
    """Test model_registry.yaml loader."""

    def test_load_default_registry(self) -> None:
        models = load_registry("config/model_registry.yaml")
        assert len(models) >= 4
        ids = [m.id for m in models]
        assert "reasoning-primary" in ids
        assert "coder-primary" in ids
        assert "vision-primary" in ids

    def test_duplicate_id_raises_error(self) -> None:
        tmp_file = Path(tempfile.mkdtemp()) / "invalid.yaml"
        tmp_file.write_text(
            """
models:
  - id: dupe-model
    engine: vllm
    path: /path/1
    task_tags: [code]
  - id: dupe-model
    engine: ollama
    path: /path/2
    task_tags: [document]
            """
        )
        with pytest.raises(ValueError, match="Duplicate model ID"):
            load_registry(tmp_file)

    def test_invalid_fallback_raises_error(self) -> None:
        tmp_file = Path(tempfile.mkdtemp()) / "invalid_fallback.yaml"
        tmp_file.write_text(
            """
models:
  - id: model-a
    engine: vllm
    path: /path/1
    task_tags: [code]
    fallback: non-existent-model
            """
        )
        with pytest.raises(ValueError, match="non-existent fallback"):
            load_registry(tmp_file)


class TestModelRouter:
    """Test ModelRouter task classification and dispatch."""

    @pytest.fixture
    def router(self) -> ModelRouter:
        return ModelRouter(registry_path="config/model_registry.yaml")

    def test_route_code_tag(self, router: ModelRouter) -> None:
        """Router should dispatch 'code' tag to coder model."""
        selected_id = router.route("code")
        assert selected_id == "coder-primary"

    def test_route_document_tag(self, router: ModelRouter) -> None:
        """Router should dispatch 'document' tag to reasoning model."""
        selected_id = router.route("document")
        assert selected_id == "reasoning-primary"

    def test_route_vision_tag(self, router: ModelRouter) -> None:
        """Router should dispatch 'vision' tag to vision model."""
        selected_id = router.route("vision")
        assert selected_id == "vision-primary"

    def test_fallback_chain(self, router: ModelRouter) -> None:
        """Router should cascade to fallback correctly."""
        fallback = router.get_fallback("coder-primary")
        assert fallback == "coder-fallback"

        chain = router.get_fallback_chain("coder-primary")
        assert chain == ["coder-primary", "coder-fallback"]

        no_fallback = router.get_fallback("coder-fallback")
        assert no_fallback is None

    def test_unknown_tag_defaults(self, router: ModelRouter) -> None:
        """Unknown task tag should fall back to general reasoning model."""
        selected_id = router.route("unknown_custom_tag")
        assert selected_id == "reasoning-primary"

    def test_task_classification(self, router: ModelRouter) -> None:
        """Verify automatic prompt category classification."""
        assert (
            router.classify_task("Write a python script to parse CSV files") == "code"
        )
        assert router.classify_task("Analyze this P&ID drawing schematic") == "vision"
        assert (
            router.classify_task("Calculate the Reynolds number and friction factor")
            == "calc"
        )
        assert (
            router.classify_task(
                "Summarize the inspection report into an approval note"
            )
            == "document"
        )
        assert router.classify_task("What is the capital of France?") == "general_qa"
