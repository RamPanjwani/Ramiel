"""Egress Monitor — real-time network activity watcher.

Polls OS-level network connections via psutil, flags any non-loopback
outbound connection, and logs violations to the egress log directory.

This is the cornerstone of Ramiel's sovereignty proof: the monitor runs
continuously and provides live evidence that zero external calls are made
during the entire session.

References:
    - Rules.md §1.1: Zero runtime network egress.
    - Architecture.md §2 step 9: Continuous egress monitoring.
    - PRD.md §6.5: Zero-egress proof acceptance criterion.
"""

from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import psutil
import structlog

logger = structlog.get_logger(__name__)

# Addresses considered safe (loopback / internal-only).
_LOOPBACK_PREFIXES = ("127.", "::1", "0.0.0.0", "::")


def _is_loopback(addr: str) -> bool:
    """Check whether an address is loopback / unbound."""
    return any(addr.startswith(p) for p in _LOOPBACK_PREFIXES) or addr == ""


class EgressViolation:
    """Record of a single outbound connection attempt."""

    def __init__(
        self,
        remote_addr: str,
        remote_port: int,
        pid: int | None,
        process_name: str,
        timestamp: str,
    ) -> None:
        self.remote_addr = remote_addr
        self.remote_port = remote_port
        self.pid = pid
        self.process_name = process_name
        self.timestamp = timestamp

    def to_dict(self) -> dict[str, Any]:
        return {
            "remote_addr": self.remote_addr,
            "remote_port": self.remote_port,
            "pid": self.pid,
            "process_name": self.process_name,
            "timestamp": self.timestamp,
        }


class EgressMonitor:
    """Background network egress monitor.

    Usage::

        monitor = EgressMonitor()
        monitor.start()       # spawns background polling thread
        ...
        monitor.violations    # list of EgressViolation dicts
        monitor.stop()
    """

    def __init__(
        self,
        poll_interval: float = 1.0,
        log_dir: str | Path = "logs/egress",
    ) -> None:
        self.poll_interval = poll_interval
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.running: bool = False
        self.total_checks: int = 0
        self.violations: list[dict[str, Any]] = []

        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()

    # ---- lifecycle --------------------------------------------------------

    def start(self) -> None:
        """Start the background polling thread."""
        if self.running:
            return
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._poll_loop, daemon=True, name="egress-monitor"
        )
        self.running = True
        self._thread.start()
        logger.info("egress_monitor.started", interval=self.poll_interval)

    def stop(self) -> None:
        """Signal the polling thread to stop."""
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5.0)
        self.running = False
        logger.info(
            "egress_monitor.stopped",
            total_checks=self.total_checks,
            violations_count=len(self.violations),
        )

    # ---- core loop --------------------------------------------------------

    def _poll_loop(self) -> None:
        """Continuously poll network connections."""
        while not self._stop_event.is_set():
            try:
                self._check_connections()
            except Exception:
                logger.exception("egress_monitor.poll_error")
            self._stop_event.wait(self.poll_interval)

    def _check_connections(self) -> None:
        """Inspect active network connections for non-loopback remotes."""
        self.total_checks += 1
        connections = psutil.net_connections(kind="inet")

        for conn in connections:
            if conn.raddr:
                remote_ip = conn.raddr.ip
                if not _is_loopback(remote_ip):
                    violation = self._record_violation(conn)
                    logger.warning(
                        "egress_monitor.VIOLATION",
                        **violation.to_dict(),
                    )

    def _record_violation(self, conn: Any) -> EgressViolation:
        """Build a violation record and persist it."""
        proc_name = ""
        try:
            if conn.pid:
                proc = psutil.Process(conn.pid)
                proc_name = proc.name()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            proc_name = "<unknown>"

        violation = EgressViolation(
            remote_addr=conn.raddr.ip,
            remote_port=conn.raddr.port,
            pid=conn.pid,
            process_name=proc_name,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        self.violations.append(violation.to_dict())
        self._persist_violation(violation)
        return violation

    def _persist_violation(self, violation: EgressViolation) -> None:
        """Append violation to the egress log file."""
        log_file = self.log_dir / "network_activity.log"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(violation.to_dict()) + "\n")

    # ---- query interface --------------------------------------------------

    def get_status(self) -> dict[str, Any]:
        """Return current monitor status for API consumption."""
        return {
            "running": self.running,
            "total_checks": self.total_checks,
            "violation_count": len(self.violations),
            "violations": self.violations,
            "status": "clean" if not self.violations else "VIOLATION_DETECTED",
        }
