"""Logging setup for production and Railway."""
from __future__ import annotations

import logging


def configure_logging(level: str = "INFO") -> None:
    """Configure structured-enough console logging for bot operations."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
