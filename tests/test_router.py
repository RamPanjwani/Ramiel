"""Model Router Tests — Phase 2 placeholder.

TODO(Phase 2): Test tag-based model dispatch, fallback chains, VRAM checks.
"""

import pytest


class TestModelRouter:
    """Placeholder for model router tests."""

    @pytest.mark.skip(reason="Phase 2 — not yet implemented")
    def test_route_code_tag(self) -> None:
        """Router should dispatch 'code' tag to coder model."""

    @pytest.mark.skip(reason="Phase 2 — not yet implemented")
    def test_fallback_chain(self) -> None:
        """Router should cascade to fallback on OOM."""

    @pytest.mark.skip(reason="Phase 2 — not yet implemented")
    def test_unknown_tag_defaults(self) -> None:
        """Unknown task tag should fall back to reasoning model."""
