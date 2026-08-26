"""Sandbox policy — resource and network constraints for code execution.

Loads sandbox limits from config/tool_permissions.yaml and exposes them
as typed constants for the code_sandbox tool.

Phase 0: config loader only.
Phase 3+: consumed by code_sandbox.py when launching Docker containers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass(frozen=True)
class SandboxPolicy:
    """Immutable sandbox resource policy."""

    cpu_limit: str = "2.0"
    memory_limit: str = "4g"
    timeout_seconds: int = 60
    network_mode: str = "none"  # NON-NEGOTIABLE — Rules.md §1.5
    temp_dir: str = "/tmp/sandbox_scratch"
    allowed_languages: list[str] = field(default_factory=lambda: ["python", "bash"])


def load_sandbox_policy(
    config_path: str | Path = "config/tool_permissions.yaml",
) -> SandboxPolicy:
    """Parse sandbox section from tool_permissions.yaml."""
    path = Path(config_path)
    if not path.exists():
        return SandboxPolicy()

    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    sandbox = raw.get("sandbox", {})
    return SandboxPolicy(
        cpu_limit=str(sandbox.get("cpu_limit", "2.0")),
        memory_limit=str(sandbox.get("memory_limit", "4g")),
        timeout_seconds=int(sandbox.get("timeout_seconds", 60)),
        network_mode=str(sandbox.get("network_mode", "none")),
        temp_dir=str(sandbox.get("temp_dir", "/tmp/sandbox_scratch")),
        allowed_languages=list(sandbox.get("allowed_languages", ["python", "bash"])),
    )
