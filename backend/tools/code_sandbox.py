"""Code Sandbox Execution Tool for Ramiel.

Phase 3: Tool Layer.
Executes generated code in an ephemeral, resource-capped Docker container with
strict network isolation (--network none) per Rules.md §1.5 and Architecture.md §7.
"""

from __future__ import annotations

import asyncio
import os
import shutil
import tempfile
import time
from pathlib import Path
from typing import Any

import structlog

from backend.security.sandbox_policy import SandboxPolicy, load_sandbox_policy

logger = structlog.get_logger(__name__)


class CodeSandbox:
    """Network-isolated execution sandbox for running code securely."""

    def __init__(
        self,
        config_path: str | Path = "config/tool_permissions.yaml",
        policy: SandboxPolicy | None = None,
    ) -> None:
        self.policy = policy or load_sandbox_policy(config_path)

    async def execute(
        self,
        code: str,
        language: str = "python",
        timeout: int | None = None,
    ) -> dict[str, Any]:
        """Execute source code in an isolated container and capture outputs.

        Args:
            code: The code string to execute.
            language: Programming language ('python' or 'bash').
            timeout: Optional override for execution timeout in seconds.

        Returns:
            Dictionary containing:
                - 'stdout': Standard output string.
                - 'stderr': Standard error string.
                - 'exit_code': Process exit status integer.
                - 'duration_ms': Total execution time in milliseconds.
                - 'timed_out': Boolean flag indicating if timeout was exceeded.
                - 'network_isolated': Boolean confirming --network none was enforced.
        """
        exec_timeout = timeout or self.policy.timeout_seconds
        start_time = time.perf_counter()

        if language not in self.policy.allowed_languages:
            return {
                "stdout": "",
                "stderr": f"Language '{language}' is not permitted by sandbox policy.",
                "exit_code": 1,
                "duration_ms": 0.0,
                "timed_out": False,
                "network_isolated": True,
            }

        # Check if Docker is available
        has_docker = shutil.which("docker") is not None

        if has_docker:
            result = await self._execute_docker(code, language, exec_timeout)
        else:
            logger.warning(
                "sandbox.docker_not_found",
                msg="Running in local fallback subprocess mode",
            )
            result = await self._execute_local_fallback(code, language, exec_timeout)

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        result["duration_ms"] = duration_ms
        return result

    async def _execute_docker(
        self,
        code: str,
        language: str,
        timeout: int,
    ) -> dict[str, Any]:
        """Execute code using Docker with --network none."""
        temp_dir = tempfile.mkdtemp(prefix="ramiel_sandbox_")
        try:
            ext = ".py" if language == "python" else ".sh"
            code_path = Path(temp_dir) / f"code{ext}"
            code_path.write_text(code, encoding="utf-8")

            # Non-negotiable network isolation: --network none
            cmd = [
                "docker",
                "run",
                "--rm",
                "--network",
                self.policy.network_mode,  # MUST be "none"
                f"--cpus={self.policy.cpu_limit}",
                f"--memory={self.policy.memory_limit}",
                "-v",
                f"{temp_dir}:/sandbox:ro",
                "python:3.12-slim",
                "python3" if language == "python" else "bash",
                f"/sandbox/code{ext}",
            ]

            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(
                    proc.communicate(), timeout=float(timeout)
                )
                return {
                    "stdout": stdout_bytes.decode("utf-8", errors="replace"),
                    "stderr": stderr_bytes.decode("utf-8", errors="replace"),
                    "exit_code": proc.returncode or 0,
                    "timed_out": False,
                    "network_isolated": True,
                }
            except asyncio.TimeoutError:
                try:
                    proc.kill()
                except ProcessLookupError:
                    pass
                return {
                    "stdout": "",
                    "stderr": f"Execution timed out after {timeout} seconds.",
                    "exit_code": -1,
                    "timed_out": True,
                    "network_isolated": True,
                }
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    async def _execute_local_fallback(
        self,
        code: str,
        language: str,
        timeout: int,
    ) -> dict[str, Any]:
        """Fallback execution when Docker is unavailable in local test environments."""
        temp_dir = tempfile.mkdtemp(prefix="ramiel_local_exec_")
        try:
            ext = ".py" if language == "python" else ".sh"
            code_path = Path(temp_dir) / f"code{ext}"
            code_path.write_text(code, encoding="utf-8")

            executable = "python" if language == "python" else "bash"
            # Strip dangerous environment variables
            clean_env = {
                k: v
                for k, v in os.environ.items()
                if k in ("PATH", "SYSTEMROOT", "TEMP", "TMP", "PYTHONPATH")
            }

            proc = await asyncio.create_subprocess_exec(
                executable,
                str(code_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=clean_env,
                cwd=temp_dir,
            )

            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(
                    proc.communicate(), timeout=float(timeout)
                )
                return {
                    "stdout": stdout_bytes.decode("utf-8", errors="replace"),
                    "stderr": stderr_bytes.decode("utf-8", errors="replace"),
                    "exit_code": proc.returncode or 0,
                    "timed_out": False,
                    "network_isolated": False,
                }
            except asyncio.TimeoutError:
                try:
                    proc.kill()
                except ProcessLookupError:
                    pass
                return {
                    "stdout": "",
                    "stderr": f"Execution timed out after {timeout} seconds.",
                    "exit_code": -1,
                    "timed_out": True,
                    "network_isolated": False,
                }
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
