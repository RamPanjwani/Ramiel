"""Structured Logging Configuration for Ramiel.

Phase 0 & 1: Single Model & Basic Chat.
Configures structlog and standard library logging for structured JSON/console output
to local log files without remote telemetry per Rules.md §1.8 and §2.1.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import structlog


def setup_logging(
    log_level: str = "INFO",
    log_file: str | None = "logs/audit/ramiel.log",
) -> None:
    """Configure structured logging for the Ramiel backend.

    Args:
        log_level: The logging severity threshold ('DEBUG', 'INFO', 'WARNING', 'ERROR').
        log_file: Optional path to an output log file on disk.
    """
    level = getattr(logging, log_level.upper(), logging.INFO)

    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]

    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(str(log_path), encoding="utf-8")
        handlers.append(file_handler)

    # Configure root standard logger
    logging.basicConfig(
        format="%(message)s",
        level=level,
        handlers=handlers,
        force=True,
    )

    # Structlog processors pipeline
    processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ]

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
