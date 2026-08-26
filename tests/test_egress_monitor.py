"""Egress Monitor Tests — Phase 0 key deliverable.

Validates that:
1. Monitor reports zero violations with loopback-only connections.
2. A deliberate outbound connection attempt gets caught and flagged.
3. Violation records are correctly structured and persisted.

Per AGENTS.md: this test is MANDATORY after any change to
backend/security/egress_monitor.py or backend/security/.
"""

from __future__ import annotations

import json
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

from backend.security.egress_monitor import EgressMonitor, _is_loopback

# ---------------------------------------------------------------------------
# Unit tests for helper functions
# ---------------------------------------------------------------------------


class TestIsLoopback:
    """Test the loopback address checker."""

    def test_ipv4_loopback(self) -> None:
        assert _is_loopback("127.0.0.1") is True

    def test_ipv4_loopback_variant(self) -> None:
        assert _is_loopback("127.0.0.53") is True

    def test_ipv6_loopback(self) -> None:
        assert _is_loopback("::1") is True

    def test_unbound_ipv4(self) -> None:
        assert _is_loopback("0.0.0.0") is True

    def test_unbound_ipv6(self) -> None:
        assert _is_loopback("::") is True

    def test_empty_string(self) -> None:
        assert _is_loopback("") is True

    def test_external_ip(self) -> None:
        assert _is_loopback("8.8.8.8") is False

    def test_private_ip(self) -> None:
        assert _is_loopback("192.168.1.1") is False

    def test_public_ip(self) -> None:
        assert _is_loopback("104.26.10.1") is False


# ---------------------------------------------------------------------------
# Integration tests for the monitor
# ---------------------------------------------------------------------------


class TestEgressMonitorClean:
    """Test monitor reports clean status when only loopback exists."""

    def test_clean_status_on_init(self) -> None:
        monitor = EgressMonitor(log_dir=tempfile.mkdtemp())
        assert monitor.violations == []
        assert monitor.total_checks == 0
        assert monitor.running is False

    def test_get_status_clean(self) -> None:
        monitor = EgressMonitor(log_dir=tempfile.mkdtemp())
        status = monitor.get_status()
        assert status["status"] == "clean"
        assert status["violation_count"] == 0

    @patch("backend.security.egress_monitor.psutil.net_connections")
    def test_loopback_only_no_violations(self, mock_conns: MagicMock) -> None:
        """Simulate connections that are all loopback — no violations."""
        conn = MagicMock()
        conn.raddr = MagicMock()
        conn.raddr.ip = "127.0.0.1"
        conn.raddr.port = 8000
        mock_conns.return_value = [conn]

        monitor = EgressMonitor(log_dir=tempfile.mkdtemp())
        monitor._check_connections()

        assert monitor.total_checks == 1
        assert len(monitor.violations) == 0

    @patch("backend.security.egress_monitor.psutil.net_connections")
    def test_no_remote_addr_no_violation(self, mock_conns: MagicMock) -> None:
        """Connections with no raddr (listening sockets) are safe."""
        conn = MagicMock()
        conn.raddr = None
        mock_conns.return_value = [conn]

        monitor = EgressMonitor(log_dir=tempfile.mkdtemp())
        monitor._check_connections()

        assert len(monitor.violations) == 0


class TestEgressMonitorViolation:
    """Test monitor catches external connections."""

    @patch("backend.security.egress_monitor.psutil.net_connections")
    def test_external_connection_flagged(self, mock_conns: MagicMock) -> None:
        """Deliberate external IP is caught and recorded."""
        conn = MagicMock()
        conn.raddr = MagicMock()
        conn.raddr.ip = "8.8.8.8"
        conn.raddr.port = 443
        conn.pid = 1234
        mock_conns.return_value = [conn]

        log_dir = tempfile.mkdtemp()
        monitor = EgressMonitor(log_dir=log_dir)

        with patch("backend.security.egress_monitor.psutil.Process") as mock_proc:
            mock_proc.return_value.name.return_value = "test-process"
            monitor._check_connections()

        assert len(monitor.violations) == 1
        v = monitor.violations[0]
        assert v["remote_addr"] == "8.8.8.8"
        assert v["remote_port"] == 443
        assert v["process_name"] == "test-process"

    @patch("backend.security.egress_monitor.psutil.net_connections")
    def test_violation_persisted_to_log(self, mock_conns: MagicMock) -> None:
        """Violation is written to the log file."""
        conn = MagicMock()
        conn.raddr = MagicMock()
        conn.raddr.ip = "104.26.10.1"
        conn.raddr.port = 80
        conn.pid = 5678
        mock_conns.return_value = [conn]

        log_dir = tempfile.mkdtemp()
        monitor = EgressMonitor(log_dir=log_dir)

        with patch("backend.security.egress_monitor.psutil.Process") as mock_proc:
            mock_proc.return_value.name.return_value = "suspicious"
            monitor._check_connections()

        log_file = Path(log_dir) / "network_activity.log"
        assert log_file.exists()
        with open(log_file, encoding="utf-8") as f:
            line = json.loads(f.readline())
        assert line["remote_addr"] == "104.26.10.1"

    @patch("backend.security.egress_monitor.psutil.net_connections")
    def test_status_shows_violation(self, mock_conns: MagicMock) -> None:
        """get_status reports VIOLATION_DETECTED after a catch."""
        conn = MagicMock()
        conn.raddr = MagicMock()
        conn.raddr.ip = "8.8.4.4"
        conn.raddr.port = 53
        conn.pid = None
        mock_conns.return_value = [conn]

        monitor = EgressMonitor(log_dir=tempfile.mkdtemp())
        monitor._check_connections()

        status = monitor.get_status()
        assert status["status"] == "VIOLATION_DETECTED"
        assert status["violation_count"] == 1


class TestEgressMonitorLifecycle:
    """Test start/stop lifecycle."""

    def test_start_and_stop(self) -> None:
        monitor = EgressMonitor(poll_interval=0.1, log_dir=tempfile.mkdtemp())
        monitor.start()
        assert monitor.running is True
        time.sleep(0.3)
        monitor.stop()
        assert monitor.running is False
        assert monitor.total_checks >= 1
