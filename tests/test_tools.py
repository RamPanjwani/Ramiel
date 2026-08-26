"""Tool Layer Tests — Phase 3 placeholder.

TODO(Phase 3): Test file I/O permissions, sandbox network isolation,
               spreadsheet operations, tool registry dispatch.
"""

import pytest


class TestScopedFileIO:
    """Placeholder for scoped file I/O tests."""

    @pytest.mark.skip(reason="Phase 3 — not yet implemented")
    def test_read_within_allowed_root(self) -> None:
        """Reading from allowed roots should succeed."""

    @pytest.mark.skip(reason="Phase 3 — not yet implemented")
    def test_read_outside_allowed_root_blocked(self) -> None:
        """Reading from disallowed paths should raise PermissionError."""


class TestCodeSandbox:
    """Placeholder for code sandbox tests."""

    @pytest.mark.skip(reason="Phase 3 — not yet implemented")
    def test_sandbox_network_none(self) -> None:
        """Sandbox must enforce --network none."""

    @pytest.mark.skip(reason="Phase 3 — not yet implemented")
    def test_sandbox_timeout(self) -> None:
        """Code exceeding timeout should be killed."""


class TestSpreadsheet:
    """Placeholder for spreadsheet tool tests."""

    @pytest.mark.skip(reason="Phase 3 — not yet implemented")
    def test_read_excel(self) -> None:
        """Should read .xlsx into structured dict."""
