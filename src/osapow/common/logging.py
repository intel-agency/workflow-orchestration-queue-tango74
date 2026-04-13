"""Structured logging configuration for OS-APOW.

Configures Python logging with StreamHandler for stdout output.
When running in Docker, stdout is captured by `docker logs`.

Features:
- Structured log format with timestamp, level, and sentinel ID
- Stdout-only logging (per S-10: no FileHandler)
- Each log line stamped with unique sentinel identifier
"""

import logging
import sys


def configure_logging(sentinel_id: str = "", level: int = logging.INFO) -> logging.Logger:
    """Configure structured logging for the application.

    Args:
        sentinel_id: Unique sentinel identifier for multi-node tracing.
        level: Logging level (default: INFO).

    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger("osapow")

    if logger.handlers:
        return logger  # Already configured

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    prefix = f"[{sentinel_id}] " if sentinel_id else ""
    formatter = logging.Formatter(
        f"{prefix}%(asctime)s %(levelname)-8s %(name)s  %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    handler.setFormatter(formatter)

    logger.setLevel(level)
    logger.addHandler(handler)

    return logger
