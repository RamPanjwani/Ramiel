"""Scoped File I/O Tool for Ramiel.

Phase 3: Tool Layer.
Provides directory-scoped filesystem operations (read, write, list) strictly
validated against allowed root boundaries defined in config/tool_permissions.yaml.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class ScopedFileIO:
    """Filesystem operations restricted to permitted directories per tool_permissions.yaml."""

    def __init__(
        self,
        config_path: str | Path = "config/tool_permissions.yaml",
        workspace_root: str | Path = ".",
    ) -> None:
        self.workspace_root = Path(workspace_root).resolve()
        self.config_path = Path(config_path)
        self.allowed_read_roots: list[Path] = []
        self.allowed_write_roots: list[Path] = []
        self._load_permissions()

    def _load_permissions(self) -> None:
        """Parse filesystem permission boundaries from YAML config."""
        if not self.config_path.exists():
            # Default fallback paths if config is missing
            self.allowed_read_roots = [
                (self.workspace_root / "data/kb_raw").resolve(),
                (self.workspace_root / "data/uploads").resolve(),
                (self.workspace_root / "demo_assets").resolve(),
            ]
            self.allowed_write_roots = [
                (self.workspace_root / "data/uploads").resolve(),
                (self.workspace_root / "logs/audit").resolve(),
            ]
            return

        with open(self.config_path, encoding="utf-8") as f:
            raw: dict[str, Any] = yaml.safe_load(f) or {}

        fs = raw.get("filesystem", {})
        read_roots = fs.get(
            "allowed_read_roots", ["data/kb_raw", "data/uploads", "demo_assets"]
        )
        write_roots = fs.get("allowed_write_roots", ["data/uploads", "logs/audit"])

        self.allowed_read_roots = [
            (self.workspace_root / r).resolve() for r in read_roots
        ]
        self.allowed_write_roots = [
            (self.workspace_root / w).resolve() for w in write_roots
        ]

    def _validate_path(self, path: str | Path, allowed_roots: list[Path]) -> Path:
        """Ensure the target path resolves inside at least one allowed root directory."""
        target = (self.workspace_root / Path(path)).resolve()
        for root in allowed_roots:
            try:
                target.relative_to(root)
                return target
            except ValueError:
                continue
        raise PermissionError(
            f"Access denied: Path '{path}' is outside allowed root boundaries ({[str(r) for r in allowed_roots]})."
        )

    def read(self, path: str | Path) -> str:
        """Read text content from a permitted file path."""
        target = self._validate_path(path, self.allowed_read_roots)
        if not target.exists():
            raise FileNotFoundError(f"File not found: {path}")
        return target.read_text(encoding="utf-8")

    def write(self, path: str | Path, content: str) -> None:
        """Write text content to a permitted destination file path."""
        target = self._validate_path(path, self.allowed_write_roots)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def list_dir(self, path: str | Path) -> list[str]:
        """List files and subdirectories within a permitted path."""
        target = self._validate_path(path, self.allowed_read_roots)
        if not target.exists():
            raise FileNotFoundError(f"Directory not found: {path}")
        if not target.is_dir():
            raise NotADirectoryError(f"Not a directory: {path}")

        return [item.name for item in target.iterdir()]

    def exists(self, path: str | Path) -> bool:
        """Check whether a permitted path exists."""
        try:
            target = self._validate_path(path, self.allowed_read_roots)
            return target.exists()
        except PermissionError:
            return False
